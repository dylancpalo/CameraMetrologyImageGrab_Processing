# Camera metrology image acquisition and processing

This repository supports camera metrology during Mu2e tracker-station assembly. It covers the image-taking and image-analysis part of the workflow and the transfer of station-assembly measurements into the PostgreSQL database. The database is intended to hold the many measurements and derived quantities needed by the downstream metrology analysis.

## Workflow role

1. Acquire calibration and production images with the camera system, following the camera and station-assembly procedures below.
2. Run the image-grab and image-analysis scripts to identify tooling-ball images and derive camera-coordinate measurements.
3. Import the station-assembly measurement results into PostgreSQL so they can be combined with the other survey and detector datasets.
4. Use [MetrologyMain](https://github.com/dylancpalo/MetrologyMain) to combine the camera results with X-ray measurements, tracker-frame measurements, and related metrology inputs.

The station-assembly procedure is maintained in [Mu2e DocDB document 50095](https://mu2e-docdb.fnal.gov/cgi-bin/sso/ShowDocument?docid=50095). It describes how to set up the Google Sheet used to record station-assembly information and how that sheet's data is transferred into PostgreSQL. Consult the procedure when setting up or running the database import workflow.

This repository handles image acquisition and camera-data processing. It is one input to the broader metrology pipeline; it does not by itself produce the final tracker-frame alignment results.

## Contents

- `ImageGrab_Analysis.py` — image acquisition and analysis workflow for the standard tooling-ball measurements.
- `ImageGrabBig.py` — image acquisition and analysis workflow for the larger Ultem-base measurement setup.
- `CameraMetrologyInstructions.pdf` — camera setup and operating instructions.
- `Ordering.txt` — ordering notes for the measurement workflow.

The station-assembly SOP is linked above rather than copied into this repository.

## Running the scripts

The scripts were developed for the experiment's camera and analysis environment and use command-line parameters for image settings and input folders. Example invocations and the original environment notes are available in the project history and procedure documents. Confirm the camera, software, folder, and database configuration for your setup before running a production measurement.

## Related repositories

- [MetrologyMain](https://github.com/dylancpalo/MetrologyMain) combines camera measurements with the X-ray dataset and tracker-frame measurements.
- [UltemAnalysis](https://github.com/dylancpalo/UltemAnalysis) analyzes Ultem measurements for quality control and machining decisions.
- [TrackBasedAlignment](https://github.com/dylancpalo/TrackBasedAlignment) uses reconstructed tracks to study and validate tracker alignment.
