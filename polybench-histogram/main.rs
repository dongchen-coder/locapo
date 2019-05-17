use std::borrow::Borrow;
use std::cmp::Ordering;
use std::cmp;
use std::collections::BinaryHeap;
use std::collections::{BTreeMap, HashMap};
use std::env;
use std::fmt::{self, Display, Formatter};
use std::fs::File;
use std::hash::Hash;
use std::hash::Hasher;
use std::io::prelude::*;
use std::io::Error as IOError;
use std::io::{BufRead, BufReader};
use std::iter::FromIterator;
use std::num;
use std::process::exit;
use std::str::FromStr;
use std::time::{Duration, Instant};
use std::thread;


const MEGABYTE: usize = 1048576;
const KILOBYTE: usize = 1024;

enum RllError {
    BadArgs,
    BadFile,
    IOError(IOError),
}

impl From<IOError> for RllError {
    fn from(e: IOError) -> RllError {
        RllError::IOError(e)
    }
}

impl From<num::ParseIntError> for RllError {
    fn from(_: num::ParseIntError) -> RllError {
        RllError::BadArgs
    }
}


impl From<num::ParseFloatError> for RllError {
    fn from(_: num::ParseFloatError) -> RllError {
        RllError::BadArgs
    }
}

impl Display for RllError {
    fn fmt(&self, f: &mut Formatter) -> Result<(), fmt::Error> {
        match self {
            &RllError::BadArgs =>
                write!(f,
                       "Usage: {} <trace> -s <sizes...> -i <intervals...> -a <alphas...> [-v] [-d <default_lease_time>]",
                       env::args().nth(0).unwrap_or("odl".to_string())),

            &RllError::BadFile => write!(f, "Bad file format"),

            &RllError::IOError(ref e) =>
                write!(f, "An error occured while running the simulation: {}", e),
        }
    }
}

#[derive(Debug, PartialEq)]
struct PPUC<'a, K: 'a + Eq> {
    //The data itself
    data: &'a K,

    //the reuse_time that is used to generate PPUC
    reuse_time: u64,

    //The cost of increasing the data's lease to "reuse_time"
    //the amount of cache occupied over a time
    cost: u64,

    //Profit per unit of cost
    //profit is the number of hits
    //ppuc is the number of hits per unit of cache-time.
    ppuc: f64,
}

//--- Orders data from lowest to highest ---
impl<'a, K: 'a + Eq> Eq for PPUC<'a, K> {}

impl<'a, K: 'a + Ord> Ord for PPUC<'a, K> {
    fn cmp(&self, other: &PPUC<'a, K>) -> Ordering {
        // We want a min heap, so we compare "backwards"
        self.ppuc.partial_cmp(&other.ppuc).expect("PPUC should never be NaN")

            // After this point is completely arbitrary. We need a total ordering for the heap, but
            // only the PPUC actually matters.
            //TODO: shouldn't cost matter too? Lowest cost first?
            .then(self.cost.cmp(&other.cost))
            .then(self.reuse_time.cmp(&other.reuse_time))
            .then(self.data.cmp(&other.data))
    }
}

impl<'a, K: 'a + Ord> PartialOrd for PPUC<'a, K> {
    fn partial_cmp(&self, other: &PPUC<'a, K>) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}
//--- Finish ordering for ppuc ---

//max_ppuc for osl
fn max_ppuc_osl<'a, K: 'a + Ord>(datum: &'a K, rt: &RT, min_rt: u64) -> Option<PPUC<'a, K>> {
    //Get the total frequency of times this data appears
    let total_freq = rt.total();

    //for each frequency, divide by total_freq, and get the max of those values

    //Holds max_ppuc encountered
    let mut max_ppuc = PPUC {
        data: datum,
        reuse_time: 0,
        cost: 0,
        ppuc: 0.0,
    };

    //Holds previous count of frequencies
    let mut previous_freq = 0;

    //Holds previous costs
    let mut previous_costs = 0;
    let mut previous_freq2 = 0;

    //Loops reuse times from shortest to longest, MINIMUM cost
    //vector holding all reuse times
    //hashmap do Reuse Time -> frequency.
    for specific_rt in rt.reuse_times.iter() {
        //sort the vector of reuse times, shortest first.
        if specific_rt <= &min_rt {
            let freq2 = rt.reuses(*specific_rt);
            previous_freq2 += freq2;
            continue;
        }
        //the specific_rt is the possible lease time

        //The frequency is the amount of times it is accessed at this reuse time.
        let freq = rt.reuses(*specific_rt);

        //this is the amount of times the reuse_time will "miss" essentially.
        let future_times = total_freq - previous_freq - freq - previous_freq2;

        //Cost is the total amount of time it would stay in cache (accounting for lease fitting)
        let cost = (future_times + freq) * (specific_rt - min_rt) + previous_costs;

        //Calculate ppuc
        let ppuc: f64 = ((freq + previous_freq) as f64) / (cost as f64); // do not include previous freq

        //if calculated ppuc is better, use it in the PPUC
        if ppuc > max_ppuc.ppuc {
            max_ppuc.ppuc = ppuc;
            max_ppuc.reuse_time = *specific_rt;
            max_ppuc.cost = cost;
        }

        //prepare for the next loop, increment previous_costs and previous_freq
        //increment previous_costs by the basic cost of this.
        previous_costs += freq * (specific_rt - min_rt);
        previous_freq += freq;
    }

    if max_ppuc.ppuc > 0.0 {
        return Some(max_ppuc);
    } else {
        None
    }
}

//Daniel's code for Buckets Below
struct Bucket(u64, u64); //Custom bucket struct to index reuse time (takes in value, sublog bits)

impl Hash for Bucket //Turns raw indexes into bucket indexes
{
    fn hash<H: Hasher>(&self, state: &mut H) {
        convert_value_to_index(self.0, self.1).hash(state);
    }
}

impl PartialEq for Bucket //Defines equality for Bucket
{
    fn eq(&self, other: &Bucket) -> bool //Checks for equality of bucket indexes
    {
        convert_value_to_index(self.0, self.1) == convert_value_to_index(other.0, other.1)
    }
}

impl Eq for Bucket {}

impl Clone for Bucket //Defines copying for custom bucket
{
    fn clone(&self) -> Bucket //Returns a copy of the custom bucket
    {
        Bucket(self.0, self.1)
    }
}

fn convert_value_to_index(value: u64, sublog_bits: u64) -> u64 //Taken from histo.h
{
    if value < (1 << sublog_bits)
        //Ignores values too small to be bucketized
        {
            return value;
        }

    let most_significant_bit = 63 - (value.leading_zeros() as u64); //Find's value's most significant bit
    let shift = most_significant_bit - sublog_bits; //Defines shift as difference between most significant bit and sublog bits
    let mut index = value >> shift; //Sets index as value shifted by shift
    index = index & ((1 << sublog_bits) - 1); //Does a bitwise and with sublog bits number of 1's

    index + ((shift + 1) << sublog_bits) //Adds the shift + 1 shfted by the number of sublogg bits and to the index
}
//Daniel's code for Buckets Above

//Reuse time histogram for indicidual data
#[derive(Clone)]
pub struct RT {
    //number of distinct reuse times for this data
    n: u64,
    //frequencry each reuse time appears, as a hashmap
    //freq: Vec<u64>,
    freq: HashMap<Bucket, u64>,
    //where the reuse times are in freq
    pub reuse_times: Vec<u64>,

    //to save on time (adding up all frequencies etc.) the total amount of accesses to the data is stored here
    total: u64,
}

//Functions for said reuse times
impl RT {
    //create empty reuse time histogram
    pub fn new() -> RT {
        RT {
            n: 0,
            freq: HashMap::new(),
            reuse_times: Vec::new(),
            total: 0,
        }
    }

    // register an access
    pub fn access(&mut self, rt: u64) {
        self.total += 1;

        let rt_bucket = Bucket(rt, 8);

        if self.freq.contains_key(&rt_bucket) {
            let mut rt_freq = self.freq.get_mut(&rt_bucket).unwrap();
            *rt_freq += 1;
        } else {
            self.freq.insert(rt_bucket, 1);
            self.n += 1;
            self.reuse_times.push(rt);
            self.reuse_times.sort();
        }
    }

    //Get the number of reuses with a specific reuse time
    pub fn reuses(&self, rt: u64) -> u64 {
        let rt_bucket = Bucket(rt, 8);

        //HASHMAP METHOD
        if self.freq.contains_key(&rt_bucket) {
            return *self.freq.get(&rt_bucket).unwrap();
        } else {
            return 0;
        }
    }

    //Returns the total frequency of data in the reuse_time_histogram for one data
    pub fn total(&self) -> u64 {
        return self.total;
    }
}

impl Default for RT {
    fn default() -> RT {
        RT::new()
    }
}

/*Write size and miss ratio data to csv file*/
fn write_mrc_file(cache_sizes: &Vec<f64>, miss_ratios: &Vec<f64>,  csv_output_path: String) {
    //    fn write_mrc_file(sizes: &Vec<usize>, miss_ratios: &Vec<f32>, dir: &str) {
    let mut data = String::new();

    for (i, mr) in miss_ratios.iter().enumerate() {
        data.push_str(&format!("{},{}\n", cache_sizes.get(i).unwrap(), mr));
        //        data.push_str(&format!("{},{}\n", cache_sizes.get(i).unwrap() / MEGABYTE, mr));
    }

    //    let mut name: String = String::from("../../generated_mrs/");
//    let mut name: String = String::from(csv_output_path);
    //    name.push_str(&dir.to_owned());
//    name.push_str("./rll_mrc.csv");
    println!("{}", csv_output_path);
    let mut file = File::create(&format!("{}", csv_output_path)).expect("csv file could not be created!");
    file.write_all(data.as_bytes())
        .expect("Unable to write to csv file");
}

//Run function gets file and args and calls simulate
fn run() -> Result<(), RllError> {
    //Initialize
    let mut args = env::args();
    let mut sizes = vec![];
    let mut intervals = vec![];
    let mut alphas = vec![];
    let mut default_leases = vec![];
    //    let mut policies = vec![];
    let default_lease;
    let mut cutoffs = vec![];
    let mut percent_over_max = vec![];
    let mut percent_learn = vec![];
    let mut state = 0;
    let mut data_block_id_trace: Vec<usize> = vec![];
    let mut ref_id_trace: Vec<usize> = vec![];
    let mut arr_id_trace: Vec<usize> = vec![];

    let input_file = File::open(args.nth(1).ok_or(RllError::BadArgs)?)?;

    let mut reuse_times: BTreeMap<usize, RT> = BTreeMap::new();
    

//    let mut bucket:Bucket;
//    let mut hist :RT = RT::new();
    let mut trace_length: usize = 0;
    // let mut reference_count: usize = 0;
    let mut max_id: usize = 0;


    for line in BufReader::new(input_file).lines() {
        match line {
            Ok(triple) => {
                //                    println!("{}",triple);
                let split_vec: Vec<_> = triple.split([','].as_ref()).collect();

                let data_block_id = split_vec[0].parse::<usize>().unwrap();
                data_block_id_trace.push(data_block_id);
                max_id = cmp::max(max_id, data_block_id);

                let reuse_interval = split_vec[1].parse::<usize>().unwrap();
                ref_id_trace.push(reuse_interval);

                let freqency = split_vec[2].parse::<usize>().unwrap();
                arr_id_trace.push(freqency);

//                println!( "|{0: <15}| {1: <15}| {2: <15}|", "ref id", "reuse interval", "freq");
//                println!("|{0: <15}| {1: <15}| {2: <15}|", data_block_id, reuse_interval,freqency);
                let rt = reuse_times.entry(data_block_id)
                        .or_insert_with(Default::default);

                    for i in 0..freqency {
                        rt.access(reuse_interval as u64);
                    }

                    trace_length += freqency;
                }

            Err(e) => Err(RllError::IOError(e))?,
        }
    }

    println!("{}",max_id);
    // trace_length *= 10;
    // trace_length *= (max_id + 1);



   // println!( "|{0: <15}| {1: <15}| {2: <15}|", "ref id", "reuse interval", "freq");
   // for (id, _rt) in &reuse_times {

   //     for ri in _rt.reuse_times.iter() {
   //         println!("|{0: <15}| {1: <15}| {2: <15}|", id, ri,_rt.reuses(*ri));
   //     }
   // }


    //Initialize more parameters
    //    let mut v = VerbosityLevel::Silent;
    let mut help = false;
    let mut osl = false;

    //CSV params
    let mut csv = false;
    let mut csv_intervals = 0; //number of intervals to do
    let mut csv_interval_size = 0; //size of increment of interval

    let mut csv_output_path = String::from("");;

    //Get args
    // -s specifies the amount of unique elements that can be held in cache at once
    // -i specifies the interval to generate an assignment of leases
    for a in args {
        match &*a {
            "-s" => state = 1,
            "-i" => state = 2,
            "-a" => state = 3,
            //            "-v" => v = VerbosityLevel::Noisy,
            "-d" => state = 4,
            //            "-p" => state = 5,
            "-h" => help = true,
            "-c" => state = 6,
            "-o" => state = 7,
            "--osl" => osl = true,
            "--help" => help = true,
            "-g" => state = 8,

            "--csv" => csv = true,
            "-ci" => state = 9,
            "-cis" => state = 10,
//            "-t" => state = 11,
            "-output" => state = 12,
            a => match state {
                1 => sizes.push(u64::from_str(a)?),
                2 => intervals.push(u64::from_str(a)?),
                3 => alphas.push(f64::from_str(a)?),
                4 => default_leases.push(u64::from_str(a)?),
                6 => cutoffs.push(u64::from_str(a)?),
                7 => percent_over_max.push(f64::from_str(a)?),
                8 => percent_learn.push(f64::from_str(a)?),
                9 => csv_intervals = u64::from_str(a)?,
                10 => csv_interval_size = u64::from_str(a)?,
                //                11 => num_threads = u32::from_str(a)?,
                12 => csv_output_path = String::from_str(a).unwrap(),
                _ => Err(RllError::BadArgs)?,
            },
        }
    }

//    println!("{}",csv_output_path);

    //If you used "-d [number]", set that number to be the default lease time.
    //default lease otherwise is the size of the cache.
    if percent_over_max.len() <= 0 {
        percent_over_max.push(0.0);
    }

    if sizes.len() == 0 && csv {
        sizes.push(1 as u64);
    }

    if default_leases.len() > 0 {
        default_lease = default_leases[0];
    } else {
        default_lease = sizes[0];
    }

    if cutoffs.len() <= 0 {
        cutoffs.push(0);
    }

    if percent_learn.len() <= 0 {
        percent_learn.push(0.0);
    }

    //If csv is set, number of intervals and interval size increment must be specified
    if csv {
        if csv_intervals <= 0 || csv_interval_size <= 0 {
            println!("-ci and -cis args must be specified as an int values, greater than zero!");
            exit(1);
        }
    }

    if help {
        println!("---------- HELP  ----------");
        println!("rll <path_to_trace> -s <size> -i <interval> -a <alphas>");
        println!("\n-- Mandatory parameters --");
        println!("<path_to_trace> should be the path to the trace.tr file.");
        println!("-a <alphas> allows you to specify as many alphas as you want, defined in paper.");
        println!(
            "-s <size> lets you specify the size of cache. This is in data_items that it can hold."
        );
        println!("-i <interval> is the interval (in terms of accesses) on which the assignment regenerates.");
        println!("\n-- Optional parameters  --");
        println!("[-h] or [--help] to receive this message.");
        println!("[-o <percent>] changes depending on implementation. Policy 100 (described below) uses one way. OSL implementation uses it to train on a percent of data and run on the rest.");
        println!("[-g <percent>] changes (FOR OSL ONLY) the length of trace in practices on. The length it practices on is the percentage given.");
        println!("[-d <default_lease>] allows you to specify what the lease is for data not seen before/not in assignment.");
        println!("\n-- Extra parameters --");
        println!("[--osl] runs an RLL simulation. This only uses [-s, -a, -v, -o, -t, -g] parameters OR [-ci, -cis, -v, -t, -g, -o, --csv, -a], and all others will be useless for OSL.");
        println!("  *RLL ONLY* [--csv] makes you a csv file with [avg size,miss rate,largest size] information per line for each specified size, for RLL simulator.");
        println!("  *RLL ONLY* [-ci <integer>] specifies the number of intervals to get.");
        println!("  *RLL ONLY* [-cis <integer>] specifies the size of increment of each interval. -ci and -cis must be specified if using the --csv option!!");
        println!("  *RLL ONLY* [-t <integer>] specifies the number of threads to run at a time for OSL (where each thread is a simulation of a different size)");
        println!("-------- END HELP  --------");
        return Ok(());
    }


    reference_level_lease(
        trace_length,
        reuse_times,
        &data_block_id_trace,
        &ref_id_trace,
        &arr_id_trace,
        csv_output_path,
        sizes[0],
        alphas[0],
        percent_over_max[0],
        percent_learn[0],
        csv_intervals,
        csv_interval_size,
    );

    Ok(())
}

fn reference_level_lease(
    sample_trace_length: usize,
    reuse_times: BTreeMap<usize, RT>,
    trace: &Vec<usize>,
    ref_id_trace: &Vec<usize>,
    arr_id_trace: &Vec<usize>,
    csv_output_path: String,
    size: u64,
    alpha: f64,
    percent_off: f64,
    percent_learn: f64,
    csv_intervals: u64,
    csv_interval_size: u64,
) {
//    println!("Starting running of Reference Level Lease.");
    //    println!("Verbose: {:?}", verbose);
    //------
    // PART 1
    //First create the entire reuse time histogram for OSL.
    //-----
//    let mut reuse_times: BTreeMap<usize, RT> = BTreeMap::new();


    println!("sample_trace_length {}", sample_trace_length);

    let mut last_seen: BTreeMap<usize, u64> = BTreeMap::new();

    
let mut access_ratio_map:BTreeMap<usize, f64> = BTreeMap::new();
    
    let mut access_ratio:u64 = 0;


//    println!("********************************");
//    println!( "|{0: <15}| {1: <15}| {2: <15}|", "ref id", "reuse interval", "freq");
   for (id, _rt) in &reuse_times {
        access_ratio  = 0;
       for ri in _rt.reuse_times.iter() {
        access_ratio += _rt.reuses(*ri);
           // println!("|{0: <15}| {1: <15}| {2: <15}|", id, ri,);
       }
       println!("{}", access_ratio);
       access_ratio_map.insert(*id, access_ratio as f64/(sample_trace_length as f64));
   }


    //First go through every access to create the reuse_time histogram.

    //Define important variables.
    let mut clock: u64 = 0;
    let mut insert = 1;

    //if using percent off,
    let mut trace_length = 0;

    if percent_learn != 0.0 {
        //get number of accesses in trace
        for _x in trace.iter() {
            trace_length += 1;
        }
    }

    let cutoff_access = (trace_length as f64 * percent_learn) as u64;

//    println!("Started collecting reuse times for reuse time histogram.");

    // for (i, access) in trace.iter().enumerate() {
    //     if clock > cutoff_access && cutoff_access != 0 {
    //         println!("Cutoff creating histogram at access {}.", clock);
    //         break;
    //     }

//        if let Some(last) = last_seen.get_mut(&access) {
//            let last64 = *last;
//            if let Some(last_access_id) = ref_id_trace.get(last64 as usize) {
//                //last time accessed (clock time)
//
//                //create a reuse-time histogram if one does not exist
//                let rt = reuse_times
//                    .entry(*last_access_id)
//                    .or_insert_with(Default::default);
//
//                //As it says, this is the reuse time just gotten
//                let the_reuse_time = clock - last64;
//
//                //Record the reuse time
//                rt.access(the_reuse_time);
//                //modify by jiao 2018.10
//                //            rt.access_k_sublog(the_reuse_time);
//
//                //Update the B tree with the new clock time
//                *last = clock;
//
//                //do not insert the data again, prevents forever growing BTree
//                insert = 0;
//            }
//        }
//
//        //If not already seen, insert data into last_seen, otherwise set insert back to 1
//        if insert == 1 {
//            //Increment unique_data counter.
//            //COULD COUNT UNIQUE DATA HERE
//            last_seen.insert(*access, clock);
//        } else {
//            insert = 1;
//        }
//
//        //Increment clock
//        clock += 1;
    // }

//    println!("Finished getting reference level histogram.");
    //BTreeMap<usize, RT>

    //2019.2.15 added for testing
    //At this point, histogram has already been built
    //using the below nested for loop can print the histogram of each data block
    //including the reuse interval and frequency
//    println!("********************************");
//    println!( "|{0: <15}| {1: <15}| {2: <15}|", "ref id", "reuse interval", "freq");
//    for (id, _rt) in &reuse_times {
//
//        for ri in _rt.reuse_times.iter() {
//            println!("|{0: <15}| {1: <15}| {2: <15}|", id, ri,_rt.reuses(*ri));
//        }
//    }

    //-----
    // END PART 1
    //-----
    let start = Instant::now();
    //Now that reuse times are generated, run the simulator for the specified sizes
    let mut sizes = vec![];
    if csv_intervals <= 0 || csv_interval_size <= 0 {
        sizes.push(size);
    } else {
        for i in 1..csv_intervals {
            sizes.push(i * csv_interval_size);
        }
    }

    let mut size_ind = 0; //index of size to run next on a thread

    let sizes_1 = if sizes.len() == 1 { true } else { false };

    let mut miss_ratio_vec: Vec<f64> = vec![];
    let mut cache_size_vec: Vec<f64> = vec![];

    //Mingyang
    // I added this while loop to get miss ratio without simulation
    while size_ind != sizes.len() {
        let size = sizes[size_ind];
        let target_cost = size as u64 * trace.len() as u64;
        let trace_len = trace.len() as f32;
        //        let assignment: BTreeMap<usize, u64> =
        //            assign_leases_osl(&reuse_times, (target_cost) as u64, trace.len() as u64)
        //                .into_iter()
        //                .map(|(k, v): (&usize, _)| (k.clone(), v.clone()))
        //                .collect();

        let rt_histogram_map = BTreeMap::from_iter(&reuse_times);

        //Binary Heap of ppuc times, highest value on top, lowest on bottom.
        let mut ppuc_times = BinaryHeap::new();

        //for each data in the reuse time histogram map, get the max_ppuc
        //Order the ppuc by highest first to lowest.
        for (data, rt_histogram) in &rt_histogram_map {
            if let Some(ppuc) = max_ppuc_osl(data, rt_histogram.borrow(), 0) {
                ppuc_times.push(ppuc);
            }
        }

        let mut total_costs: u64 = 0;

        //--- Make the actual assignment ---
        let mut assignment = BTreeMap::new();
        let mut total_cost = 0;
        let mut total_hits = 0_f64;

        // try to get msr from histogram 
        
        //While the total_cost remains lower than the target_cost
//        !ppuc_times.is_empty();
        // Mingyang I change the while loop condition so that
        // the while loop will terminate only when ppuc stack is empty
//        while total_cost < target_cost {
        while !ppuc_times.is_empty() {
            //current highest ppuc here
            if let Some(specific_ppuc) = ppuc_times.pop() {
//                println!();
               // println!("Reference id is {:?}",*specific_ppuc.data);
               // println!("Lease assigned is {}",specific_ppuc.reuse_time);
               // println!("ppuc is {}",specific_ppuc.ppuc);
               // println!("cost is {}",specific_ppuc.cost);
               // println!();
                //I added total_hits to get miss ratio from PPUC
                total_hits += specific_ppuc.cost as f64 * specific_ppuc.ppuc;

                total_costs += specific_ppuc.cost;

                assignment.insert(*specific_ppuc.data, specific_ppuc.reuse_time);

                total_cost += specific_ppuc.cost;

                //re-do the calculation, because the ppuc times have changed, re-calculate for this data and add it.
                if let Some(ppuc) = max_ppuc_osl(
                    specific_ppuc.data,
                    rt_histogram_map[specific_ppuc.data].borrow(),
                    specific_ppuc.reuse_time,
                ) {
                    ppuc_times.push(ppuc);
                }
            } else {
                break;
            }

            for (k,v) in assignment.iter() {
                println!("{} {}", k,v);
            }


           println!();
           println!("*** Get miss ratio from PPUC ***");
           println!("Total costs: {}", total_costs);
           println!("Total costs (block) : {}", total_costs /sample_trace_length as u64);
           println!("Total hits {}", total_hits);
           let mut miss_ratio = 1_f64 - total_hits / sample_trace_length as f64;
            // I change the code here
            // average_cache_size is KB granularity, each data block is 8B so NumOfDataBlock x 8B/1024B
            let mut average_cache_size = (total_cost as f64 / (sample_trace_length as f64)) as f64 * 8_f64 /1024_f64;
//            let mut average_cache_size = (total_cost / (trace_len as u64)) as usize;
           println!("Miss ratio {}", miss_ratio);
           println!();

            miss_ratio_vec.push(miss_ratio);
            cache_size_vec.push(average_cache_size);

        }

        size_ind += 1;
    }

//    write_mrc_file(&cache_size_vec, &miss_ratio_vec, csv_output_path);
    let duration = start.elapsed();
    // println!("\nAlgorithm 1 takes: {:?}", duration);
    //if we only have 1 size and don't want to write to csv, then exit function here
    if sizes_1 {
        return;
    }
}

fn main() {
    if let Err(e) = run() {
        eprintln!("{}", e);
        drop(e);
        exit(1);
    }
}
