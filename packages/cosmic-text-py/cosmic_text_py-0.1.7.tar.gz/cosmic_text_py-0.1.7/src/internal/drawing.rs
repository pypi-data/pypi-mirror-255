use cosmic_text::Attrs;

use super::utils::pixmap_mut;


pub fn draw_text_mut(
    canvas: crate::canvas::Canvas,
    text: &str,
    x: f32,
    y: f32,
    width: f32,
    height: f32,
    font: &mut crate::font::Font,
    font_color: crate::objects::Color,
) -> Result<(), String> {
    match pixmap_mut(&mut canvas.im.write().unwrap()) {
        Some(mut pixmap) => {
            let mut buffer = font.buffer.borrow_with(&mut font.system);

            {
                let (c_width, c_height) = buffer.size();

                if (c_width - width).abs() > 0.1 || (c_height - height).abs() > 0.1 {
                    buffer.set_size(width, height);
                }
            }

            buffer.set_text(text, cosmic_text::Attrs::new(), cosmic_text::Shaping::Advanced);
            // buffer.shape_until_scroll(true);

            if buffer.redraw() {
                let background_rect = tiny_skia::Rect::from_xywh(x, y, width, height).unwrap();
                let background_paint = tiny_skia::Paint::default();
                pixmap.fill_rect(background_rect, &background_paint, tiny_skia::Transform::default(), None);

                buffer.draw(
                    &mut font.cache,
                    cosmic_text::Color::rgba(font_color.0[0], font_color.0[1], font_color.0[2], font_color.0[3]),
                    |x_i, y_i, w_i, h_i, color_i| {
                        let rect = tiny_skia::Rect::from_xywh(x_i as f32, y_i as f32, w_i as f32, h_i as f32).unwrap();

                        let paint = tiny_skia::Paint {
                            shader: tiny_skia::Shader::SolidColor(
                                tiny_skia::Color::from_rgba8(color_i.r(), color_i.g(), color_i.b(), color_i.a())
                            ),
                            ..tiny_skia::Paint::default()
                        };

                        pixmap.fill_rect(rect, &paint, tiny_skia::Transform::from_translate(x, y), None);
                    }
                );
            }

            Ok(())
        },
        None => Err("Can't get pixmap!".to_string()),
    }
}


pub fn draw_text_advance_mut(
    canvas: crate::canvas::Canvas,
    text: Vec<(&str, Attrs)>,
    x: f32,
    y: f32,
    width: f32,
    height: f32,
    font: &mut crate::font::Font
) -> Result<(), String> {
    match pixmap_mut(&mut canvas.im.write().unwrap()) {
        Some(mut pixmap) => {
            let mut buffer = font.buffer.borrow_with(&mut font.system);

            {
                let (c_width, c_height) = buffer.size();

                if (c_width - width).abs() > 0.1 || (c_height - height).abs() > 0.1 {
                    buffer.set_size(width, height);
                }
            }

            buffer.set_rich_text(text, Attrs::new(), cosmic_text::Shaping::Advanced);
            // buffer.shape_until_scroll(true);

            let background_rect = tiny_skia::Rect::from_xywh(x, y, width, height).unwrap();
            let background_paint = tiny_skia::Paint::default();
            pixmap.fill_rect(background_rect, &background_paint, tiny_skia::Transform::default(), None);

            buffer.draw(
                &mut font.cache,
                cosmic_text::Color::rgba(255, 255, 255, 255),
                |x_i, y_i, w_i, h_i, color_i| {
                    let rect = tiny_skia::Rect::from_xywh(x_i as f32, y_i as f32, w_i as f32, h_i as f32).unwrap();

                    let paint = tiny_skia::Paint {
                        shader: tiny_skia::Shader::SolidColor(
                            tiny_skia::Color::from_rgba8(color_i.r(), color_i.g(), color_i.b(), color_i.a())
                        ),
                        ..tiny_skia::Paint::default()
                    };

                    pixmap.fill_rect(rect, &paint, tiny_skia::Transform::from_translate(x, y), None);
                }
            );

            Ok(())
        },
        None => Err("Can't get pixmap!".to_string()),
    }
}
