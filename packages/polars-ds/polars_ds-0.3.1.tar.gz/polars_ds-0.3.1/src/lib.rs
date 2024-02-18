#![feature(float_gamma)]

mod graph;
mod num;
mod stats;
mod stats_utils;
mod str2;
mod utils;
use pyo3::{pymodule, types::PyModule, PyResult, Python};

#[cfg(target_os = "linux")]
use jemallocator::Jemalloc;

#[global_allocator]
#[cfg(target_os = "linux")]
static ALLOC: Jemalloc = Jemalloc;

#[pymodule]
#[pyo3(name = "_polars_ds")]
fn _polars_ds(_py: Python<'_>, _m: &PyModule) -> PyResult<()> {
    Ok(())
}

// --------------------------------------------------------------------------------------
// Shared splitting method
fn split_offsets(len: usize, n: usize) -> Vec<(usize, usize)> {
    if n == 1 {
        vec![(0, len)]
    } else {
        let chunk_size = len / n;

        (0..n)
            .map(|partition| {
                let offset = partition * chunk_size;
                let len = if partition == (n - 1) {
                    len - offset
                } else {
                    chunk_size
                };
                (partition * chunk_size, len)
            })
            .collect()
    }
}

// --------------------------------------------------------------------------------------
// Shared output types
use polars::{
    datatypes::{DataType, Field},
    error::PolarsResult,
    lazy::dsl::FieldsMapper,
};

pub fn first_field_output(fields: &[Field]) -> PolarsResult<Field> {
    Ok(fields[0].clone())
}

pub fn list_u64_output(_: &[Field]) -> PolarsResult<Field> {
    Ok(Field::new(
        "nodes",
        DataType::List(Box::new(DataType::UInt64)),
    ))
}

pub fn list_f64_output(_: &[Field]) -> PolarsResult<Field> {
    Ok(Field::new(
        "floats",
        DataType::List(Box::new(DataType::Float64)),
    ))
}

pub fn complex_output(_: &[Field]) -> PolarsResult<Field> {
    Ok(Field::new(
        "complex",
        DataType::Array(Box::new(DataType::Float64), 2),
    ))
}

pub fn list_str_output(_: &[Field]) -> PolarsResult<Field> {
    Ok(Field::new(
        "list_str",
        DataType::List(Box::new(DataType::String)),
    ))
}

pub fn float_output(fields: &[Field]) -> PolarsResult<Field> {
    FieldsMapper::new(fields).map_to_float_dtype()
}
