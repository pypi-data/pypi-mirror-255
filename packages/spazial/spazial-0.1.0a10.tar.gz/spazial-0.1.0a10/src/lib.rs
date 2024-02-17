use pyo3::prelude::*;
use rayon::prelude::*;
use std::f64::consts::PI;


#[cfg(test)]
use rand::Rng;
#[cfg(test)]
use plotters::prelude::*;

mod spatials;
mod csproc;

use crate::spatials::csstraussproc;
use crate::csproc::csstraussproc2;
use crate::csproc::csstraussproc_rhciter;

/// estimate the K-value for a set of points and a given distance
fn kest(points: &[(f64, f64)], area: f64, d: f64) -> f64 {
    let n = points.len() as f64;
    // this iterates over all points in parallel and checks for the amount of other points within the distance d
    let k_value = points.par_iter().map(|&point1| {
        // previously, this was: points[i + 1..].iter()...
        points.iter().filter(|&&point2| {
            point1 != point2 && euclidean_distance(point1, point2) < d
        }).count() as f64
    }).sum::<f64>();

    // from cskhat (Matlab)
    area * k_value / (n*n)
    // from https://github.com/astropy/astropy/blob/main/astropy/stats/spatial.py#L232C27-L232C27
    // 2.0 * area * k_value / (n * (n - 1.0))
}

/// calculate the estimated K function for a set of points and multiple distances
fn kfun(points: &[(f64, f64)], area: f64, max_d: f64) -> Vec<(f64, f64)>{
    (1..)
        .map(|i| (i as f64 / 100.0)/*percent*/ * max_d )
        .take_while(|&d| d <= max_d)
        .map(|d| (d, kest(points, area, d)))
        .collect()
}

#[pyfunction]
fn khat_test(points: Vec<Vec<f64>>, area: f64, max_d: f64) -> (Vec<f64>, Vec<f64>) {
    // convert points to tuples
    let mpoints: Vec<(f64, f64)> = points.iter().map(|point| (point[0], point[1])).collect();

    let res = kfun(&mpoints, area, max_d);

    // return a tuple of x and y values
    let x = res.iter().map(|(d, _)| *d).collect();
    let y = res.iter().map(|(_, k)| *k).collect();

    (x, y)
}

#[pyfunction]
fn lhatc_test(points: Vec<Vec<f64>>, area: f64, max_d: f64) -> (Vec<f64>, Vec<f64>) {
    // convert points to tuples
    let mpoints: Vec<(f64, f64)> = points.iter().map(|point| (point[0], point[1])).collect();

    let res = kfun(&mpoints, area, max_d);
    // sqrt(k/PI) - d, from Baddeley S.207 and Dixon 2002
    let lres: Vec<(f64, f64)> = res.iter().map(|(d, k)| (*d, (k / PI).sqrt() - d)).collect();

    // convert tuples to vectors
    // return a tuple of x and y values
    let x = lres.iter().map(|(d, _)| *d).collect();
    let y = lres.iter().map(|(_, l)| *l).collect();

    (x, y)
}

#[pyfunction]
fn lhat_test(points: Vec<Vec<f64>>, area: f64, max_d: f64) -> (Vec<f64>, Vec<f64>) {
    // convert points to tuples
    let mpoints: Vec<(f64, f64)> = points.iter().map(|point| (point[0], point[1])).collect();

    let res = kfun(&mpoints, area, max_d);
    // sqrt(k/PI) - d, from Baddeley S.207 and Dixon 2002
    let lres: Vec<(f64, f64)> = res.iter().map(|(d, k)| (*d, (k / PI).sqrt())).collect();

    // convert tuples to vectors
    // return a tuple of x and y values
    let x = lres.iter().map(|(d, _)| *d).collect();
    let y = lres.iter().map(|(_, l)| *l).collect();

    (x, y)
}



fn euclidean_distance(point1: (f64, f64), point2: (f64, f64)) -> f64 {
    let (x1, y1) = point1;
    let (x2, y2) = point2;
    ((x2 - x1).powi(2) + (y2 - y1).powi(2)).sqrt()
}



/// A Python module implemented in Rust.
#[pymodule]
fn spazial(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(khat_test, m)?)?;
    m.add_function(wrap_pyfunction!(lhatc_test, m)?)?;
    m.add_function(wrap_pyfunction!(lhat_test, m)?)?;

    m.add_function(wrap_pyfunction!(csstraussproc, m)?)?;
    m.add_function(wrap_pyfunction!(csstraussproc2, m)?)?;
    m.add_function(wrap_pyfunction!(csstraussproc_rhciter, m)?)?;
    Ok(())
}


#[cfg(test)]
fn generate_random_points(n: usize, width: f64, height: f64) -> Vec<(f64, f64)> {
    let mut rng = rand::thread_rng();
    (0..n).map(|_| (rng.gen::<f64>() * width, rng.gen::<f64>() * height)).collect()
}

#[cfg(test)]
fn plot_points(points: &[(f64, f64)], file_name: &str) -> Result<(), Box<dyn std::error::Error>> {
    let root = BitMapBackend::new(file_name, (640, 480)).into_drawing_area();
    root.fill(&WHITE)?;

    let (x_min, x_max) = points.iter().fold((f64::INFINITY, f64::NEG_INFINITY), |(min, max), &(x, _)| {
        (min.min(x), max.max(x))
    });

    let (y_min, y_max) = points.iter().fold((f64::INFINITY, f64::NEG_INFINITY), |(min, max), &(_, y)| {
        (min.min(y), max.max(y))
    });

    let mut chart = ChartBuilder::on(&root)
        .caption("Ripley's K-Funktion Test", ("sans-serif", 30).into_font())
        .margin(5)
        .x_label_area_size(30)
        .y_label_area_size(30)
        .build_cartesian_2d(x_min..x_max, y_min..y_max)?;

    chart.configure_mesh().draw()?;
    chart.draw_series(PointSeries::of_element(
        points.iter().copied(),
        3,
        &RED,
        &|coord, size, style| {
            EmptyElement::at(coord) + Circle::new((0, 0), size, style.filled())
        },
    ))?;

    root.present()?;
    Ok(())
}

#[cfg(test)]
fn plot_values(
    values: &[(f64, f64)],
    file_name: &str,
    title: &str,
    x_title: &str,
    y_title: &str)
-> Result<(), Box<dyn std::error::Error>>
{


    let (x_min, x_max) = values.iter().fold((f64::INFINITY, f64::NEG_INFINITY), |(min, max), &(x, _)| {
        (min.min(x), max.max(x))
    });

    let (y_min, y_max) = values.iter().fold((f64::INFINITY, f64::NEG_INFINITY), |(min, max), &(_, y)| {
        (min.min(y), max.max(y))
    });
    let root = BitMapBackend::new(file_name, (640, 480)).into_drawing_area();
    root.fill(&WHITE)?;
    let mut chart = ChartBuilder::on(&root)
        .caption(title, ("sans-serif", 30).into_font())
        .margin(25)
        .x_label_area_size(30)
        .y_label_area_size(30)
        .build_cartesian_2d(x_min..x_max, y_min..y_max)?;

    chart.configure_mesh().x_desc(x_title).y_desc(y_title).draw()?;

    let data = Vec::from(values);
    chart.draw_series(LineSeries::new(data, &RED))?;

    // add labels to x and y axes

    root.present()?;
    Ok(())
}


#[test]
fn test_ripleys() -> Result<(), Box<dyn std::error::Error>>{
    let points = generate_random_points(100, 100.0, 100.0);
    let area = 10000.0; // 100x100 Fläche
    let t = 10.0;

    let k_value = kest(&points, area, t);
    println!("Ripley's K-Funktion Wert: {}", k_value);

    plot_points(&points, "test_ripleys_points.png")?;

    Ok(())
}

#[test]
fn test_ripleys_func() -> Result<(), Box<dyn std::error::Error>>  {
    let w = 500.0;
    let h = 500.0;
    let points = generate_random_points(500, w, h);
    let area = w*h; // 100x100 Fläche
    let max_d = 50.0;
    let k_values: Vec<(f64, f64)> = kfun(&points, area, max_d);
    let l_values: Vec<(f64, f64)> = k_values.iter().map(|(d, k)| (*d, (k / PI).sqrt())).collect();
    // for i in 1..100 {
    //     let d = i as f64 * max_d / 100.0;
    //     l_values[i].1 -= d;
    // }


    plot_values(&k_values, "test_ripleys_func_K.png", "K-Function", "d", "K")?;
    plot_values(&l_values, "test_ripleys_func_L.png", "L-Function", "d", "L")?;

    plot_points(&points, "test_ripleys_func_points.png")?;

    Ok(())
}