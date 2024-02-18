use std::io::Cursor;
use pyo3::prelude::*;
use pyo3::types::PyBytes;
use image::io::Reader;


#[pyfunction]
fn shrink_image_buffer(py: Python, src_image_buffer: &[u8], max_width: u32, max_height: u32) -> PyResult<PyObject> {
    let reader = Reader::new(Cursor::new(src_image_buffer))
        .with_guessed_format()
        .unwrap();
    let format = reader.format().unwrap();

    let src_image = reader.decode().unwrap();
    let dst_image = src_image.thumbnail(max_width, max_height);

    let mut dst_image_buffer = Cursor::new(Vec::new());
    dst_image.write_to(&mut dst_image_buffer, format).unwrap();
    Ok( PyBytes::new(py, &dst_image_buffer.get_ref()).into())
}

#[pymodule]
fn shrink_img(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(shrink_image_buffer, m)?)?;
    Ok(())
}
