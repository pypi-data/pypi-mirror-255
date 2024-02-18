use pyo3::prelude::*;


#[derive(FromPyObject)]
pub struct Color(pub [u8; 4]);
