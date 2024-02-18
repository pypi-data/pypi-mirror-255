use pyo3::prelude::*;
use rand::Rng;
use rand::distributions::{Distribution, Uniform};
use std::f64;


pub fn csbinproc_rect(x_min: f64, x_max: f64, y_min: f64, y_max: f64) -> (f64, f64) {
    let mut rng = rand::thread_rng();
    let x_dist = Uniform::new(x_min, x_max);
    let y_dist = Uniform::new(y_min, y_max);

    (x_dist.sample(&mut rng), y_dist.sample(&mut rng))
}

fn euclidean_distance(a: (f64, f64), b: (f64, f64)) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

fn is_valid_point(points: &[(f64, f64)], candidate: (f64, f64), delta: f64, c: f64, rng: &mut impl Rng) -> bool {
    let mut close_points = 0;

    for point in points {
        if euclidean_distance(*point, candidate) <= delta {
            close_points += 1;
        }
    }

    // the more points are within the neighbourhood, the less likely an acceptance
    if close_points == 0 || rng.gen::<f64>() <= c.powi(close_points as i32) {
        true
    } else {
        false
    }
}

#[pyfunction]
pub fn csstraussproc(rect_area: (f64, f64), delta: f64, n: usize, c: f64, max_iterations: i32) -> Vec<(f64, f64)> {
    let mut rng = rand::thread_rng();
    let (x_min, y_min) = (0.0, 0.0);
    let (x_max, y_max) = rect_area;

    if delta <= 0.0 {
        panic!("Delta must be positive.");
    }
    if !(0.0..=1.0).contains(&c) {
        panic!("C must be in the interval [0,1].");
    }

    let mut points: Vec<(f64, f64)> = Vec::with_capacity(n);
    points.push(csbinproc_rect(x_min, x_max, y_min, y_max));

    let mut iterations = 0;

    while points.len() < n {
        let candidate_point = csbinproc_rect(x_min, x_max, y_min, y_max);
        if is_valid_point(&points, candidate_point, delta, c, &mut rng) {
            points.push(candidate_point);
        }

        iterations += 1;
        if iterations > max_iterations {
            // display a warning, containing the desired number of poitns and the actual point count
            println!("Warning: Maximum number of iterations reached. {}/{} points were generated.", points.len(), n);
            println!("> Equivalent fracture intensity: {}", points.len() as f64 / (x_max * y_max));
            break;
        }
    }

    points
}