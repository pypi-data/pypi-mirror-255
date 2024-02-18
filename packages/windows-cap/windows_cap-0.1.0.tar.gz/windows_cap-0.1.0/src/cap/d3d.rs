use super::Result;
use windows::core::{ComInterface, Interface};
use windows::Graphics::Capture::*;
use windows::Graphics::DirectX::Direct3D11::*;
use windows::Win32::Graphics::{Direct3D::*, Direct3D11::*, Dxgi::*};
use windows::Win32::System::WinRT::Direct3D11::*;

unsafe fn create_d3d_device_with_type(
    driver_type: D3D_DRIVER_TYPE,
    flags: D3D11_CREATE_DEVICE_FLAG,
    device: *mut Option<ID3D11Device>,
) -> Result<(), windows::core::Error> {
    D3D11CreateDevice(
        None,
        driver_type,
        None,
        flags,
        None,
        D3D11_SDK_VERSION,
        Some(device),
        None,
        None,
    )
}

pub unsafe fn create_d3d_device() -> Result<ID3D11Device> {
    let mut device = None;
    let mut result = create_d3d_device_with_type(
        D3D_DRIVER_TYPE_HARDWARE,
        D3D11_CREATE_DEVICE_BGRA_SUPPORT,
        &mut device,
    );
    if let Err(error) = &result {
        if error.code() == DXGI_ERROR_UNSUPPORTED {
            result = create_d3d_device_with_type(
                D3D_DRIVER_TYPE_WARP,
                D3D11_CREATE_DEVICE_BGRA_SUPPORT,
                &mut device,
            );
        }
    }
    result?;
    Ok(device.unwrap())
}

pub fn create_direct3d_device(d3d_device: &ID3D11Device) -> Result<IDirect3DDevice> {
    let dxgi_device: IDXGIDevice = d3d_device.cast()?;
    let inspectable = unsafe { CreateDirect3D11DeviceFromDXGIDevice(&dxgi_device)? };
    Ok(inspectable.cast()?)
}

pub fn get_d3d_interface_from_object<S: Interface + ComInterface, R: Interface + ComInterface>(
    object: &S,
) -> Result<R> {
    let access: IDirect3DDxgiInterfaceAccess = object.cast()?;
    let object = unsafe { access.GetInterface::<R>()? };
    Ok(object)
}

pub fn create_dx_texture_2d(
    d3d_device: &ID3D11Device,
    d3d_context: &ID3D11DeviceContext,
    frame: &Direct3D11CaptureFrame,
) -> Result<ID3D11Texture2D> {
    let source_texture: ID3D11Texture2D = get_d3d_interface_from_object(&frame.Surface()?)?;
    let mut desc = D3D11_TEXTURE2D_DESC::default();
    unsafe {
        source_texture.GetDesc(&mut desc);
    }
    desc.BindFlags = 0;
    desc.MiscFlags = 0;
    desc.Usage = D3D11_USAGE_STAGING;
    desc.CPUAccessFlags = D3D11_CPU_ACCESS_READ.0 as u32;
    let copy_texture = {
        let mut texture = None;
        unsafe {
            d3d_device.CreateTexture2D(&desc, None, Some(&mut texture))?;
        }
        texture.unwrap()
    };

    unsafe {
        d3d_context.CopyResource(Some(&copy_texture.cast()?), Some(&source_texture.cast()?));
    }

    Ok(copy_texture)
}

pub fn get_bits_from_texture_2d(
    d3d_context: &ID3D11DeviceContext,
    texture: &ID3D11Texture2D,
    width: usize,
    height: usize,
    buffer: &mut Vec<u8>,
) -> Result<()> {
    let mut desc = D3D11_TEXTURE2D_DESC::default();
    unsafe {
        texture.GetDesc(&mut desc as *mut _);
    }

    let resource: ID3D11Resource = texture.cast()?;
    let mut mapped: D3D11_MAPPED_SUBRESOURCE = D3D11_MAPPED_SUBRESOURCE::default();
    unsafe {
        d3d_context.Map(
            Some(&resource.clone()),
            0,
            D3D11_MAP_READ,
            0,
            Some(&mut mapped),
        )?;
    }

    // Get a slice of bytes
    let slice: &[u8] = unsafe {
        std::slice::from_raw_parts(
            mapped.pData as *const _,
            (desc.Height * mapped.RowPitch) as usize,
        )
    };

    let bytes_per_pixel = 4;
    let margin = desc.Width as usize - width;
    let col_offset = (margin / 2) * bytes_per_pixel as usize;
    for row in (desc.Height as usize - height)..desc.Height as usize {
        let slice_begin = (row * mapped.RowPitch as usize) as usize + col_offset;
        let slice_end = slice_begin + (width * bytes_per_pixel) as usize;
        buffer.extend_from_slice(&slice[slice_begin..slice_end]);
    }
    assert!(buffer.len() == width * height * bytes_per_pixel);

    unsafe {
        d3d_context.Unmap(Some(&resource), 0);
    }
    Ok(())
}
