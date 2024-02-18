use tiny_skia::*;

pub fn point(x: f32, y: f32) -> Point {
    Point::from_xy(x, y)
}


// does not copy the image
pub fn pixmap_mut(image: &mut image::RgbaImage) -> Option<PixmapMut<'_>> {
    let (w, h) = image.dimensions();
    PixmapMut::from_bytes(image, w, h)
}
