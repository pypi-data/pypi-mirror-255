pub mod font;
pub mod canvas;
pub mod drawing;
pub mod objects;
pub mod paint;
pub mod internal;

use pyo3::prelude::*;


#[pymodule]
fn cosmic_text_py(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<canvas::Canvas>()?;
    m.add_class::<font::Font>()?;
    m.add_class::<paint::Paint>()?;

    m.add_function(wrap_pyfunction!(drawing::draw_text, m)?)?;
    m.add_function(wrap_pyfunction!(drawing::draw_text_advance, m)?)?;

    Ok(())
}
