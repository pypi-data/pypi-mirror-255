use binding::{drop_manually_allocated_pcwstr, new_pcwstr_from_str};
use d3d::*;
use error::Error;
use windows::{
    core::{IInspectable, PCWSTR},
    Foundation::TypedEventHandler,
    Graphics::{
        Capture::*,
        DirectX::{Direct3D11::*, *},
        SizeInt32,
    },
    Win32::{
        Foundation::{HWND, RECT},
        Graphics::Direct3D11::*,
        System::WinRT::Graphics::Capture::IGraphicsCaptureItemInterop,
        UI::{
            HiDpi::GetDpiForWindow,
            WindowsAndMessaging::{FindWindowW, GetClientRect},
        },
    },
};
use pyo3::prelude::*;

mod binding;
mod d3d;
mod error;

type Result<T, E = Error> = std::result::Result<T, E>;

pub(crate) struct Frame {
    frame: Direct3D11CaptureFrame,
    size: SizeInt32,
}

#[pyclass]
pub struct WindowCapture {
    last_size: SizeInt32,
    client_size: SizeInt32,
    rx: std::sync::mpsc::Receiver<Frame>,
    session: GraphicsCaptureSession,
    frame_pool: Direct3D11CaptureFramePool,
    _capture_item: GraphicsCaptureItem,
    device: IDirect3DDevice,
    d3d_context: ID3D11DeviceContext,
    d3d_device: ID3D11Device,
    _hwnd: HWND,
    buffer: Vec<u8>,
}

unsafe impl Send for WindowCapture {}

#[pymethods]
impl WindowCapture {
    #[new]
    #[pyo3(signature = (windowname, classname = None))]
    pub fn __new__(windowname: &str, classname: Option<&str>) -> PyResult<Self> {
        let hwnd = unsafe {
            let classname = classname
                .map(|s| new_pcwstr_from_str(s))
                .unwrap_or(PCWSTR::null());
            let windowname = new_pcwstr_from_str(windowname);
            let hwnd = FindWindowW(classname, windowname);

            if !classname.is_null() {
                drop_manually_allocated_pcwstr(classname);
            }
            drop_manually_allocated_pcwstr(windowname);

            hwnd
        };

        if hwnd.0 == 0 {
            Err(Error::WindowNotFound)?
        } else {
            Ok(Self::new(hwnd)?)
        }
    }

    pub fn start_capture(&self) -> PyResult<()> {
        self.session.StartCapture().map_err(Error::from)?;
        Ok(())
    }

    #[getter]
    pub fn client_size(&self) -> PyResult<(i32, i32)> {
        Ok((self.client_size.Width, self.client_size.Height))
    }

    /// Get the next frame from the capture session
    pub fn next<'a>(&mut self) -> PyResult<&[u8]> {
        self.buffer.clear();
        let frame = self.rx.recv().unwrap();
        let size = frame.frame.ContentSize().map_err(Error::from)?;
        if size != self.last_size {
            self.last_size = size;
            self.frame_pool.Recreate(
                &self.device,
                DirectXPixelFormat::B8G8R8A8UIntNormalized,
                1,
                size,
            ).map_err(Error::from)?;
        }

        if self.client_size != frame.size {
            self.client_size = frame.size;
            self.buffer.reserve(self.client_size.Width as usize * self.client_size.Height as usize * 4);
        }

        let texture = create_dx_texture_2d(&self.d3d_device, &self.d3d_context, &frame.frame)?;
        get_bits_from_texture_2d(
            &self.d3d_context, 
            &texture,
            frame.size.Width as usize,
            frame.size.Height as usize,
            &mut self.buffer,
        )?;
        drop(texture);
        frame.frame.Close().map_err(Error::from)?;

        Ok(&self.buffer)
    }
}

impl WindowCapture {
    fn new(hwnd: HWND) -> Result<Self> {
        assert!(hwnd.0 != 0, "Window handle cannot be null");

        let d3d_device = unsafe { create_d3d_device()? };
        let d3d_context = unsafe { d3d_device.GetImmediateContext()? };
        let device = create_direct3d_device(&d3d_device)?;
        // Obtain the IGraphicsCaptureItemInterop activation factory
        let interop: IGraphicsCaptureItemInterop =
            windows::core::factory::<GraphicsCaptureItem, IGraphicsCaptureItemInterop>()?;

        // Create a GraphicsCaptureItem for the window using its HWND
        let capture_item = unsafe { interop.CreateForWindow::<_, GraphicsCaptureItem>(hwnd)? };

        // Define the capture frame pool and create a session
        let frame_pool = Direct3D11CaptureFramePool::CreateFreeThreaded(
            &device,
            DirectXPixelFormat::B8G8R8A8UIntNormalized,
            1,                    // Buffer count (1 is typically sufficient for most scenarios)
            capture_item.Size()?, // Specify the initial size of the capture item
        )?;
        let session: GraphicsCaptureSession = frame_pool.CreateCaptureSession(&capture_item)?;
        session.SetIsBorderRequired(true)?;
        session.SetIsCursorCaptureEnabled(false)?;

        let (tx, rx) = std::sync::mpsc::channel();

        let handler = TypedEventHandler::<Direct3D11CaptureFramePool, IInspectable>::new(
            move |sender: &Option<Direct3D11CaptureFramePool>, _: &Option<IInspectable>| {
                let frame_pool = sender.as_ref().unwrap();
                let frame = frame_pool.TryGetNextFrame()?;
                
                tx.send(Frame {
                    frame,
                    size: get_client_rect(hwnd)
                })
                .unwrap();
                Ok(())
            },
        );
        frame_pool.FrameArrived(&handler)?;

        let client_size = get_client_rect(hwnd);

        Ok(Self {
            last_size: capture_item.Size()?,
            client_size: get_client_rect(hwnd),
            rx,
            session,
            frame_pool,
            _capture_item: capture_item,
            device,
            d3d_context,
            d3d_device,
            _hwnd: hwnd,
            buffer: Vec::with_capacity(client_size.Width as usize * client_size.Height as usize * 4),
        })
    }
}

impl Drop for WindowCapture {
    fn drop(&mut self) {
        self.session.Close().ok();
        self.frame_pool.Close().ok();
        self.device.Close().ok();
    }
}

fn get_client_rect(hwnd: HWND) -> SizeInt32 {
    let dpi = unsafe { GetDpiForWindow(hwnd) } as i32;
    let mut client_rect = RECT::default();
    unsafe { GetClientRect(hwnd, &mut client_rect).unwrap() };
    let width = client_rect.right - client_rect.left;
    let height = client_rect.bottom - client_rect.top;
    let width_dpi = ((width * dpi) as f32 / 96.0) as i32;
    let height_dpi = ((height * dpi) as f32 / 96.0) as i32;
    SizeInt32 { Width: width_dpi, Height: height_dpi }
}