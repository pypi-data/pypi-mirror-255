use pyo3::prelude::*;
use rand::Rng;
// use plotters::prelude::*;

const PI: f64 = std::f64::consts::PI;

fn generate_point(width: f64, height: f64) -> [f64;2] {
    let mut rng = rand::thread_rng();
    [rng.gen_range(0.0..1.0) * width, rng.gen_range(0.0..1.0) * height]
}

fn distance(point1: &[f64;2], point2: &[f64;2]) -> f64 {
    ((point1[0] - point2[0]).powi(2) + (point1[1] - point2[1]).powi(2)).sqrt()
}
fn unpack_p(p: &[f64;2]) -> (f64, f64) {
    (p[0], p[1])
}

fn r2d(r: f64) -> f64 {
    r * 180.0 / PI
}

fn d2r(d: f64) -> f64 {
    d * PI / 180.0
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

    // Debug Output if necessary
    // // create plot of distances and deltas
    // let x = distances;
    // let y = deltas;
    // let root = BitMapBackend::new("scatter.png", (640, 480)).into_drawing_area();
    // root.fill(&WHITE).unwrap();

    // let min_x = x.iter().cloned().fold(f64::INFINITY, f64::min) as f32;
    // let max_x = x.iter().cloned().fold(f64::NEG_INFINITY, f64::max)as f32;
    // let min_y = y.iter().cloned().fold(f64::INFINITY, f64::min)as f32;
    // let max_y = y.iter().cloned().fold(f64::NEG_INFINITY, f64::max)as f32;

    // let mut chart = ChartBuilder::on(&root)
    //     .caption("Scatter Plot", ("Arial", 50).into_font())
    //     .margin(5)
    //     .build_cartesian_2d(min_x..max_x, min_y..max_y).unwrap();

    // chart.configure_mesh().draw().unwrap();

    // chart.draw_series(PointSeries::of_element(
    //     x.iter().zip(y.iter()).map(|(&x, &y)| (x as f32, y as f32)), // convert to f32
    //     5,
    //     ShapeStyle::from(&RED).filled(),
    //     &|coord, size, style| {
    //         EmptyElement::at(coord)
    //             + Circle::new((0, 0), size, style)
    //     },
    // )).unwrap();


    points
}

fn circle_area(r: f64, a0: f64, a1: f64) -> f64 {
    0.5 * (a1 - a0) * r.powi(2)
}

#[pyfunction]
pub fn bohmann_process(
    width: f64,
    height: f64,
    r_range: Vec<f64>,
    r_lambda: Vec<[f64;2]>,
    r_delta: Vec<[f64;2]>,
    impact_pos: [f64;2],
    c: f64,
    i_max: i64) -> Vec<[f64;2]>
{
    if !(0.0..=1.0).contains(&c) {
        panic!("C must be in the interval [0,1].");
    }

    // generate data structure and add first point
    let mut rng = rand::thread_rng();
    let mut points = vec![generate_point(width, height)];

    // keep track of iterations
    let mut iterations: i64;

    // keep track of distances and deltas
    let mut distances: Vec<f64> = Vec::new();
    let mut deltas: Vec<f64> = Vec::new();

    // split impact point for easier calculations
    let ix = impact_pos[0];
    let iy = impact_pos[1];

    let dr = r_range[1] - r_range[0];

    for i in 0..r_range.len() {
        let r0: f64 = r_range[i];
        let r1: f64 = if i < r_range.len() - 1 {
            r_range[i+1]
        } else {
            r_range[i] + dr
        };

        let rc = (r0 + r1) / 2.0;

        // calculate valid angles at the radii
        let mut a0 = -f64::atan(iy / r0);
        let mut a1 = PI/2.0 + f64::atan(ix / r0);

        if r0 < (ix.powi(2) + iy.powi(2)).sqrt() {
            a0 = 0.0;
            a1 = 2.0*PI;
        }

        // area of current radius band
        let a_current = circle_area(r1, a0, a1) - circle_area(r0, a0, a1);
        // interpolate max nr from r_lambda
        let lambda = interpolate(&r_lambda, rc);
        // this is the desired number of points for the current radius
        let nr = (lambda*a_current) as i32;
        // this is the actual amoutn of points for the current radius
        let mut nr_actual = 0;
        // reset global iterations
        iterations = 0;

        // println!("Radius: {} - {} - {} - {}", r0, r1, rc, nr);
        // println!("Angles: {} - {}", r2d(a0), r2d(a1));
        while nr_actual < nr{
            // create random radius and angle between boundaries
            let r = rng.gen_range(r0..r1);
            let a = rng.gen_range(a0..a1);
            // create a candidate point
            let candidate = [impact_pos[0] + r * f64::cos(a), impact_pos[1] + r * f64::sin(a)];


            let mut too_close = false;
            let mut inhibition_count = 0;

            // find the distance of the candidate to the impact position
            let dist  = distance(&candidate, &impact_pos);
            distances.push(dist);
            // use interpolation, to find the delta (rhc) at a given distance
            let delta = interpolate(&r_delta, dist);
            deltas.push(delta);

            // count points that would be too close
            for point in &points {
                if distance(&candidate, point) <= delta {
                    too_close = true;
                    inhibition_count += 1;
                }
            }

            // for each point would be closer than distance, c increases exponentially by inhibition_count
            if !too_close || rng.gen::<f64>() <= c.powi(inhibition_count) {
                points.push(candidate);
                nr_actual += 1;
            }

            iterations += 1;
            if iterations >= i_max {
                println!("Warning: Maximum number of iterations reached. {}/{} points were generated.", nr_actual, nr);
                break;
            }
        }
    }

    // remove all points that are outside the boundaries
    points.retain(|&p| p[0] >= 0.0 && p[0] <= width && p[1] >= 0.0 && p[1] <= height);
    // // Debug Output if necessary
    // // create plot of distances and deltas
    // let x = distances;
    // let y = deltas;
    // let root = BitMapBackend::new("scatter.png", (640, 480)).into_drawing_area();
    // root.fill(&WHITE).unwrap();

    // let min_x = x.iter().cloned().fold(f64::INFINITY, f64::min) as f32;
    // let max_x = x.iter().cloned().fold(f64::NEG_INFINITY, f64::max)as f32;
    // let min_y = y.iter().cloned().fold(f64::INFINITY, f64::min)as f32;
    // let max_y = y.iter().cloned().fold(f64::NEG_INFINITY, f64::max)as f32;

    // let mut chart = ChartBuilder::on(&root)
    //     .caption("Scatter Plot", ("Arial", 50).into_font())
    //     .margin(5)
    //     .build_cartesian_2d(min_x..max_x, min_y..max_y).unwrap();

    // chart.configure_mesh().draw().unwrap();

    // chart.draw_series(PointSeries::of_element(
    //     x.iter().zip(y.iter()).map(|(&x, &y)| (x as f32, y as f32)), // convert to f32
    //     5,
    //     ShapeStyle::from(&RED).filled(),
    //     &|coord, size, style| {
    //         EmptyElement::at(coord)
    //             + Circle::new((0, 0), size, style)
    //     },
    // )).unwrap();
    points
}