# process_cuwb_data

Tools for reading, processing, and writing CUWB data

## Setup

This project uses Poetry. Please make sure Poetry is installed before continuing.

1. Copy `.env.template` to `.env` and update variables


2. Install packages

    `just install`

    You may need to install pybind11 `brew install pybind11`
    And you may need to manually install cython and numpy `pip install numpy cython pythran`

## Tasks

### Export pickled UWB data

Working with Honeycomb's UWB endpoint can be painfully slow. For that reason there is an option to export pickled UWB data and provide that to subsequent inference commands.

     process_cuwb_data \
        fetch-cuwb-data \
        --environment greenbrier \
        --start 2021-04-20T9:00:00-0500 \
        --end 2021-04-20T9:05:00-0500 \
        --annonymize


### Export pickled Motion Feature data

The tray carry model doesn't read raw UWB data. It reads a version of UWB data that has been prepared for inference. This feature data can be generated and fed into subsequent commands.

     process_cuwb_data \
        fetch-motion-features \
        --environment greenbrier \
        --start 2021-05-27T14:13:00 \
        --end 2021-05-27T14:15:00 \
        --cuwb-data ./output/uwb_data/uwb-greenbrier-20210527-141300-20210527-141500.pkl \
        --annonymize


### Generate Tray Centroids

Tray centroids, or tray positions, are the most likely locations of a tray's shelf or at-rest position. Tray locations are used, for example, to determine when someone is picking a tray up off the shelf as opposed to picking up a tray from a workstation. Note that tray locations are computed based on the window of time provided to the function. If the function ran on 10 minutes of classroom data, it'd likely produce a different idea of tray's shelf locations than if the function was run on 9 hours of classroom activity.  

    process_cuwb_data \
        estimate-tray-centroids \
        --environment dahlia \
        --start 2023-01-06T07:30:00-0800 \
        --end 2023-01-06T17:00:00-0800 \
        --cuwb-data ./output/uwb_data/uwb-dahlia-20230106-153000-20230107-010000.pkl \
        --tray-carry-model ./output/models/tray_carry_model_v2.pkl


### Train Tray Detection Model
The tray detection model is a simple RandomForest model. It's used by many of the available methods in the library.

1. Download/create [ground_truth_tray_carry.csv](https://docs.google.com/spreadsheets/d/1NLQ_7Cj432T1AXFcbKLX3P6LGGGRAklxMTjtBYS_xhA/edit?usp=sharing) to `./downloads/ground_truth_tray_carry.csv`
```
    curl -L 'https://docs.google.com/spreadsheets/d/1NLQ_7Cj432T1AXFcbKLX3P6LGGGRAklxMTjtBYS_xhA/export?exportFormat=csv' --output ./downloads/ground_truth_tray_carry.csv
```

2. Generate pickled groundtruth features dataframe from ground_truth_tray_carry.csv

This will download data from Honeycomb and prepare it for the next step of feeding it into a model for training.

```
    process_cuwb_data \
        generate-tray-carry-groundtruth \
        --groundtruth-csv ./downloads/ground_truth_tray_carry.csv
```

3. Train and pickle Tray Carry Detection Model using pickled groundtruth features

```
    process_cuwb_data \
        train-tray-carry-model \
        --groundtruth-features ./output/groundtruth/2021-05-13T12:53:26_tray_carry_groundtruth_features.pkl
```

### Infer Tray Carries

1. Infer Tray Interactions using a pickled Tray Carry Detection Model
    1. Use the model you've trained by following the steps to **Train Tray Detection Model**
    2. Or, download the latest model:
```
    curl -L 'https://drive.google.com/uc?export=download&id=1U3QV5TNZCs_GF-L2GO8t-h-BeJs7cCph' --output ./output/models/tray_carry_model_v2.pkl
```   

### Infer Tray Interaction 

This outputs a list of tray carries (CARRY FROM SHELF / CARRY TO SHELF / CARRY UNKNOWN / etc.) and describe the person, the material, the length of the carry, and median distance between the nearest person and tray over the course of the event

     process_cuwb_data \
         infer-tray-interactions \
         --environment greenbrier \
         --start 2021-04-20T9:00:00-0500 \
         --end 2021-04-20T9:05:00-0500 \
         --tray-carry-model ./output/models/2021-05-13T14:49:32_tray_carry_model.pkl \
         --cuwb-data ./output/uwb_data/uwb-greenbrier-20210420-140000-20210420-140500.pkl
        
    (or, instead of --cuwb-datam, use) --motion-feature-data ./output/feature_data/motion-features-greenbrier-20210527-141300-20210527-141500.pkl
    (optionally, supply tray positions/centroids. Note, these locations should ALWAYS be provided if attempting to infer tray interactions on a partial window of classroom time.) --tray-positions-csv ./output/locations/2023-01-19T15:57:12_tray_centroids.csv

#### Supply Pose Track Inference to Tray Interaction Inference

Use Pose Tracks when determining nearest person to tray carry events.

Pose Inferences need to be sourced in a local directory. The pose directory can be supplied via CLI options.
   
     process_cuwb_data \
         infer-tray-interactions \
         --environment greenbrier \
         --start 2021-04-20T9:00:00-0500 \
         --end 2021-04-20T9:05:00-0500 \
         --tray-carry-model ./output/models/2021-05-13T14:49:32_tray_carry_model.pkl \
         --cuwb-data ./output/uwb_data/uwb-greenbrier-20210420-140000-20210420-140500.pkl \
         --pose-inference-id 3c2cca86ceac4ab1b13f9f7bfed7834e

### Infer Tray Events

This is a more standardized version/output of Tray Interactions. It's the format used by the Material Events API. It's input includes the TrayInteractions CSV from **Infer Tray Interaction**

*Note, `time_zone` is a required parameter. It's used to construct strings with times that will be read by end users. We will not default this to timezone that may be invalid.*

     process_cuwb_data \
         infer-tray-events \
         --environment dahliasf \
         --tray-interactions ./output/inference/tray_interactions/2023-01-23T15:28:30_tray_interactions.csv \
         --time_zone US/Pacific

### Infer Material Events

This generates a list of "complete" material events. A complete material event starts with a Carry From Shelf and ends with a Carry To Shelf. The Material Events output also includes a list of cameras that best capture the arc of the material event. 

*Note, `time_zone` is a required parameter. It's used to construct strings with times that will be read by end users. We will not default this to timezone that may be invalid.*

     process_cuwb_data \
         infer-material-events \
         --environment dahliasf \
         --tray-events ./output/inference/tray_events/2023-01-23T22:05:02_tray_events.csv \
         --timezone US/Pacific
