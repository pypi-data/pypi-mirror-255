use pyo3::prelude::*;
use rand::Rng;
use plotters::prelude::*;


fn generate_point(width: f64, height: f64) -> [f64;2] {
    let mut rng = rand::thread_rng();
    [rng.gen::<f64>() * width, rng.gen::<f64>() * height]
}

fn distance(point1: &[f64;2], point2: &[f64;2]) -> f64 {
    ((point1[0] - point2[0]).powi(2) + (point1[1] - point2[1]).powi(2)).sqrt()
}
fn unpack_p(p: &[f64;2]) -> (f64, f64) {
    (p[0], p[1])
}
/// Function that can linearly interpolate an x value from a set of xy points.
pub fn interpolate(xy: &[[f64;2]], x0: f64) -> f64 {
    let mut y0 = std::f64::NAN;

    if x0 <= xy[0][0] {
        let (x1, y1) = unpack_p(&xy[0]);
        let (x2, y2) = unpack_p(&xy[1]);
        let t = (x0 - x1) / (x2 - x1);
        y0 = y1 + t * (y2 - y1);
    } else if x0 >= xy[xy.len() - 1][0] {
        let (x1, y1) = unpack_p(&xy[xy.len() - 2]);
        let (x2, y2) = unpack_p(&xy[xy.len() - 1]);
        let t = (x0 - x1) / (x2 - x1);
        y0 = y1 + t * (y2 - y1);
    } else {
        for i in 0..xy.len() - 1 {
            let (x1, y1) = unpack_p(&xy[i]);
            let (x2, y2) = unpack_p(&xy[i + 1]);

            if x0 >= x1 && x0 <= x2 {
                let t = (x0 - x1) / (x2 - x1);
                y0 = y1 + t * (y2 - y1);
                break;
            }
        }
    }

    y0
}
#[pyfunction]
pub fn csstraussproc2(width: f64, height: f64, delta: f64, n: usize, c: f64, i_max: i32) -> Vec<[f64;2]> {
    if delta <= 0.0 {
        panic!("Delta must be positive.");
    }

    if !(0.0..=1.0).contains(&c) {
        panic!("C must be in the interval [0,1].");
    }

    let mut rng = rand::thread_rng();
    let mut points = Vec::with_capacity(n);
    points.push(generate_point(width, height));

    let mut iterations = 0;

    while points.len() < n {
        let candidate = generate_point(width, height);
        let mut too_close = false;
        let mut inhibition_count = 0;

        for point in &points {
            if distance(&candidate, point) <= delta {
                too_close = true;
                inhibition_count += 1;
            }
        }

        if !too_close || rng.gen::<f64>() <= c.powi(inhibition_count) {
            points.push(candidate);
        }

        iterations += 1;
        if iterations >= i_max {
            println!("Warning: Maximum number of iterations reached. {}/{} points were generated.", points.len(), n);
            println!("> Equivalent fracture intensity: {}", points.len() as f64 / (width * height));
            break;
        }
    }

    points
}

#[pyfunction]
pub fn csstraussproc_rhciter(
    width: f64,
    height: f64,
    xy_delta: Vec<[f64;2]>,
    impact_pos: [f64;2],
    n: usize,
    c: f64,
    i_max: i32) -> Vec<[f64;2]>
{
    if !(0.0..=1.0).contains(&c) {
        panic!("C must be in the interval [0,1].");
    }


    let mut rng = rand::thread_rng();
    let mut points = Vec::with_capacity(n);
    points.push(generate_point(width, height));

    let mut iterations = 0;

    let mut distances: Vec<f64> = Vec::new();
    let mut deltas: Vec<f64> = Vec::new();

    while points.len() < n {
        let candidate = generate_point(width, height);
        let mut too_close = false;
        let mut inhibition_count = 0;

        // find the distance of the candidate to the impact position
        let dist  = distance(&candidate, &impact_pos);
        distances.push(dist);
        // use interpolation, to find the delta (rhc) at a given distance
        let delta = interpolate(&xy_delta, dist);
        deltas.push(delta);

        for point in &points {
            if distance(&candidate, point) <= delta {
                too_close = true;
                inhibition_count += 1;
            }
        }

        // for each point that is closer than distance, c increases exponentially by inhibition_count
        if !too_close || rng.gen::<f64>() <= c.powi(inhibition_count) {
            points.push(candidate);
        }

        iterations += 1;
        if iterations >= i_max {
            println!("Warning: Maximum number of iterations reached. {}/{} points were generated.", points.len(), n);
            println!("> Equivalent fracture intensity: {}", points.len() as f64 / (width * height));
            break;
        }
    }

    // create plot of distances and deltas
    let x = distances;
    let y = deltas;
    let root = BitMapBackend::new("scatter.png", (640, 480)).into_drawing_area();
    root.fill(&WHITE).unwrap();

    let min_x = x.iter().cloned().fold(f64::INFINITY, f64::min) as f32;
    let max_x = x.iter().cloned().fold(f64::NEG_INFINITY, f64::max)as f32;
    let min_y = y.iter().cloned().fold(f64::INFINITY, f64::min)as f32;
    let max_y = y.iter().cloned().fold(f64::NEG_INFINITY, f64::max)as f32;

    let mut chart = ChartBuilder::on(&root)
        .caption("Scatter Plot", ("Arial", 50).into_font())
        .margin(5)
        .build_cartesian_2d(min_x..max_x, min_y..max_y).unwrap();

    chart.configure_mesh().draw().unwrap();

    chart.draw_series(PointSeries::of_element(
        x.iter().zip(y.iter()).map(|(&x, &y)| (x as f32, y as f32)), // convert to f32
        5,
        ShapeStyle::from(&RED).filled(),
        &|coord, size, style| {
            EmptyElement::at(coord)
                + Circle::new((0, 0), size, style)
        },
    )).unwrap();


    points
}