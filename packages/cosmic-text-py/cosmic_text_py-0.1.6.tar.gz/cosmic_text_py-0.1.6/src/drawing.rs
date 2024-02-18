use pyo3::{prelude::*, types::PyTuple};

use crate::internal::drawing::{draw_text_mut, draw_text_advance_mut};


#[pyfunction]
pub fn draw_text(
    _py: Python,
    canvas: crate::canvas::Canvas,
    text: &str,
    x: f32,
    y: f32,
    width: f32,
    height: f32,
    font: &mut crate::font::Font,
    font_color: crate::objects::Color
) -> PyResult<()> {
    draw_text_mut(canvas, text, x, y, width, height, font, font_color)
    .map_err(|e| {
        PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
            "Failed to draw text: {}",
            e
        ))
    })
}


#[pyfunction]
pub fn draw_text_advance(
    _py: Python,
    canvas: crate::canvas::Canvas,
    text: &PyTuple,
    x: f32,
    y: f32,
    width: f32,
    height: f32,
    font: &mut crate::font::Font,
) -> PyResult<()> {
    let text = text.into_iter().map(|item| {
        let inner_tuple: &PyTuple = item.downcast().unwrap();

        let string_part: &str = inner_tuple.get_item(0).unwrap().extract().unwrap();
        let color_part: crate::objects::Color = inner_tuple.get_item(1).unwrap().extract().unwrap();

        let attrs = cosmic_text::Attrs::new();

        (string_part, attrs.color(cosmic_text::Color::rgba(color_part.0[0], color_part.0[1], color_part.0[2], color_part.0[3])))
    }).collect();

    draw_text_advance_mut(canvas, text,  x, y, width, height, font)
    .map_err(|e| {
        PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
            "Failed to draw text: {}",
            e
        ))
    })
}
