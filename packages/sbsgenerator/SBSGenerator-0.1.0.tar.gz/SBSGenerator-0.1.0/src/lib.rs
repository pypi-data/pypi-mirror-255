use std::collections::HashMap;
use numpy::PyArray;
use pyo3::types::PyList;
use pyo3::Python;
use pyo3::prelude::*;
use std::fs::File;
use std::io::{BufRead, BufReader, Read, Seek, SeekFrom};

#[pyfunction]
fn parse_vcf_files(py: Python, vcf_files: &PyList, ref_genome: &str, context: usize) -> PyResult<PyObject> {
    let mut all_data = Vec::new();

    for vcf_file in vcf_files {
        let vcf_file_path: String = vcf_file.extract()?;
        
        // Reuse your existing read_vcf_file logic here.
        // This example assumes you modify read_vcf_file to return Vec<Vec<String>>
        // directly instead of PyObject for easier data manipulation in Rust.
        let data = read_vcf_file_contents(&vcf_file_path, &ref_genome, &context)?;
        all_data.extend(data);
    }

    // Flatten the all_data to a single Vec<String>, similar to your existing logic,
    // and then convert it to a NumPy array.
    let s = all_data.len(); // Number of mutations
    let t = if !all_data.is_empty() { all_data[0].len() } else { 0 }; // Number of attributes per mutation

    let py_objects: Vec<PyObject> = all_data.into_iter().flatten().map(|x| x.to_object(py)).collect();

    let np_array = PyArray::from_iter(py, py_objects.iter().map(|x| x.to_object(py))).reshape([s, t]).unwrap();

    Ok(np_array.to_object(py))
}

fn read_vcf_file_contents(vcf_file: &str, ref_genome: &str, context: &usize) -> PyResult<Vec<Vec<String>>> {
    let nucleotides = vec!["A", "C", "G", "T"];
    let mut data = Vec::new();

    // Open the VCF file for reading
    let file = File::open(vcf_file).map_err(|_| pyo3::exceptions::PyIOError::new_err("Failed to open the VCF file"))?;

    // Define translation dictionaries
    let mut translate_purine_to_pyrimidine: std::collections::HashMap<char, char> =
        std::collections::HashMap::new();
    translate_purine_to_pyrimidine.insert('A', 'T');
    translate_purine_to_pyrimidine.insert('G', 'C');

    let mut translate_nucleotide: std::collections::HashMap<char, char> =
        std::collections::HashMap::new();
    translate_nucleotide.insert('A', 'T');
    translate_nucleotide.insert('C', 'G');
    translate_nucleotide.insert('G', 'C');
    translate_nucleotide.insert('T', 'A');

    // Read and process each line of the VCF file
    for line in BufReader::new(file).lines() {
        let line = line.map_err(|_| pyo3::exceptions::PyIOError::new_err("Error reading line from the VCF file"))?;

        // Split the line by tabs
        let fields: Vec<&str> = line.split('\t').collect();

        // Check if the line has the required number of fields
        if fields.len() >= 10 {
            let reference_genome = fields[3];
            let mutation_type = fields[4];
            let chromosome = fields[5];
            let reference_allele = fields[8];
            let alternate_allele = fields[9];

            let translated_alternate: String = if (reference_allele == "A" || reference_allele == "G") && nucleotides.contains(&alternate_allele) {
                alternate_allele
                .chars()
                .map(|c| *translate_nucleotide.get(&c).unwrap_or(&c))
                .collect()
            } else {
                alternate_allele.to_string()
            };
            let translated_reference: String = reference_allele
                .chars()
                .map(|c| *translate_purine_to_pyrimidine.get(&c).unwrap_or(&c))
                .collect();

            // Check conditions and apply filters
            if (reference_genome == "GRCh37" || reference_genome == "GRCh38")
                && (mutation_type == "SNP" || mutation_type == "SNV")
                && nucleotides.contains(&alternate_allele)
                && (translated_reference != translated_alternate) {
                let position = fields[6].parse::<usize>().unwrap() - 1;
                let start = position.saturating_sub(context / 2);
                let end = position + context / 2 + 1;
                let total_path = format!("{}/{}/{}.txt", ref_genome, reference_genome, chromosome);
                let (left, right) = read_bytes_file_contents(&total_path, start, end)?;
                let sample = format!("{}::{}", fields[0], fields[1]);
                data.push(vec![
                    sample,
                    format!("{}[{}>{}]{}", left, translated_reference, translated_alternate, right),
                ]);
            }
        }
    }

    Ok(data)
}

fn read_bytes_file_contents(file_path: &str, start: usize, end: usize) -> PyResult<(String, String)> {
    // Open the bytes file for reading
    let mut file = File::open(file_path)
        .map_err(|_| pyo3::exceptions::PyIOError::new_err("Failed to open the bytes file"))?;

    // Seek to the desired position
    file.seek(SeekFrom::Start(start as u64))
        .map_err(|_| pyo3::exceptions::PyIOError::new_err("Error seeking to the specified position"))?;

    // Read the data from the specified position to the left and right
    let bytes_to_read = end - start;  // One character on the left, the character at the position, and one character on the right
    let mut buffer = vec![0; bytes_to_read];
    file.read_exact(&mut buffer)
        .map_err(|_| pyo3::exceptions::PyIOError::new_err("Error reading data from the file"))?;

    // Create a translation mapping
    let translation_mapping: HashMap<u8, char> = [
        (0, 'A'), (1, 'C'), (2, 'G'), (3, 'T'),
        (4, 'A'), (5, 'C'), (6, 'G'), (7, 'T'),
        (8, 'A'), (9, 'C'), (10, 'G'), (11, 'T'),
        (12, 'A'), (13, 'C'), (14, 'G'), (15, 'T'),
        (16, 'N'), (17, 'N'), (18, 'N'), (19, 'N'),
    ].iter().cloned().collect();
    let middle_index = bytes_to_read / 2;
    let result: String = buffer.iter().map(|&byte| {
        translation_mapping.get(&byte).unwrap_or(&' ').to_owned()
    }).collect();
    let result_chars: Vec<char> = result.chars().collect();
    let left = result_chars[..middle_index].iter().collect::<String>();
    let right = result_chars[middle_index + 1..].iter().collect::<String>();

    Ok((left, right))

    // Translate the integers into characters
    // let result: String = buffer.iter().map(|&byte| {
    //     translation_mapping.get(&byte).unwrap_or(&' ').to_owned()
    // }).collect();

    // Ok(result)
}


/// A Python module implemented in Rust.
#[pymodule]
fn SBSGenerator(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;
    m.add_function(wrap_pyfunction!(parse_vcf_files, m)?)?;
    Ok(())
}