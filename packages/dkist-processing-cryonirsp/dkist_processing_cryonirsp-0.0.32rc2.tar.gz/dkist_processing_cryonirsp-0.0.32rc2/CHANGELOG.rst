v0.0.31 (2024-02-06)
====================

Bugfixes
--------

- Flipping value of CDELT1 to account for the dispersion axis flip. (`#80 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/80>`__)
- Flipping dispersion axis in the final reduced data. (`#80 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/80>`__)


v0.0.30 (2024-02-02)
====================

Features
--------

- Enable intensity mode observations to be calibrated with polarized calibration data. (`#83 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/83>`__)


v0.0.29 (2024-02-01)
====================

Misc
----

- Add tasks to trial workflows enabling ASDF, dataset inventory, and movie generation. (`#88 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/88>`__)


v0.0.28 (2024-01-31)
====================

Misc
----

- Bump versions of `dkist-fits-specifications`, `dkist-data-simulator`, and `dkist-header-validator` for fits spec version 4.1.0 (`#85 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/85>`__)


v0.0.27 (2024-01-29)
====================

Features
--------

- Modify parsing to correctly detect the use of dual nested internal scanning loops, with the outer loop step size set to zero to emulate a DSP map scan. (`#79 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/79>`__)


Bugfixes
--------

- Fixed errors in the ordering of the Helioprojective Latitude and Longitude axes in the L1 headers. (`#71 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/71>`__)


v0.0.26 (2024-01-25)
====================

Misc
----

- Update version of dkist-processing-common to 5.1.0 which includes common tasks for cataloging in trial workflows. (`#87 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/87>`__)


v0.0.25 (2024-01-12)
====================

Bugfixes
--------

- Compute polarimetric noise and sensitivity values and add to L1 headers (POL_NOIS, and POL_SENS, respectively). These
  keywords are now required by the fits-spec. (`#84 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/84>`__)


Misc
----

- Update `dkist-fits-specifications` and associated (validator, simulator) to use new conditional requiredness framework. (`#84 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/84>`__)


v0.0.24 (2024-01-03)
====================

Misc
----

- Bump version of `dkist-processing-pac` to v3.0.1. No change to pipeline behavior at all. (`#82 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/82>`__)


v0.0.23 (2023-12-20)
====================

Misc
----

- Adding manual processing worker capabilities via dkist-processing-common update. (`#81 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/81>`__)


v0.0.22 (2023-12-01)
====================

Misc
----

- Use `TaskName`, task-tags, and Task-parsing flowers from `dkist-processing-common`. These had all been defined in `dkist-processing-cryonirsp`, but
  were recetly moved up to `*-common`. (`#78 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/78>`__)


v0.0.21 (2023-11-24)
====================

Misc
----

- Updates to core and common to patch security vulnerabilities and deprecations. (`#77 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/77>`__)


v0.0.20 (2023-11-22)
====================

Misc
----

- Update the FITS header specification to remove some CRYO-NIRSP specific keywords from the L1 headers. (`#76 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/76>`__)


v0.0.19 (2023-11-15)
====================

Features
--------

- Define a public API for tasks such that they can be imported directly from dkist-processing-cryonirsp.tasks (`#75 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/75>`__)


v0.0.18 (2023-11-08)
====================

Bugfixes
--------

- Removes cross-talk correction from SP science task. (`#72 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/72>`__)
- Turn on bad-pixel correction of science observe frames for science team evaluation. (`#73 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/73>`__)
- Fix computation of characteristic spectrum by removing incorrect median normalization. (`#74 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/74>`__)


v0.0.17 (2023-11-06)
====================

Features
--------

- Implement relative photometric calibration. Linearized ramp sets are normalized to counts per second. Attenuation due to Optical Density filters is compensated. Solar gain image is no longer normalized to mean of 1. Observe images are now in units of flux relative to solar center. (`#70 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/70>`__)


v0.0.16 (2023-11-02)
====================

Features
--------

- Add check to ensure calibration frames with exposure times correlated with observe frames exist and fail fast if they do not. (`#51 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/51>`__)


v0.0.15 (2023-10-17)
====================

Bugfixes
--------

- Fixed bug in SP solar gain task where lamp gain was being applied to the average solar image,
  causing the spectral transmission profile to be removed from the resulting solar gain image.
  The lamp gain is no longer applied. (`#67 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/67>`__)


Misc
----

- Complete refactorization of the SP solar gain task. (`#67 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/67>`__)


v0.0.14 (2023-10-17)
====================

Features
--------

- Modifies the linearity correction to divide the process into smaller chunks using less memory. No longer requires that entire ramp set be stored in memory at once. (`#65 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/65>`__)


v0.0.13 (2023-10-11)
====================

Misc
----

- Use latest version of dkist-processing-common (4.1.4) which adapts to the new metadata-store-api. (`#68 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/68>`__)


v0.0.12 (2023-10-06)
====================

Misc
----

- Identify ramps with only one frame as invalid and do not linearize them. (`#62 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/62>`__)


v0.0.11 (2023-10-05)
====================

Features
--------

- Removes casts and flips used when loading parameter files. The files are now changed to be in the format we want. (`#68 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/68>`__)


v0.0.10 (2023-09-29)
====================

Misc
----

- Remove and edit selected APM spans to reduce load on aggregating span data. (`#64 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/64>`__)


v0.0.9 (2023-09-29)
===================

Features
--------

- Removes all references to the FitsDataMixin and its methods, which are deprecated. Uses the new self.read() and self.write() methods with encoder and decoder support. (`#63 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/63>`__)


Misc
----

- Update pillow to address security vulnerability. (`#66 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/66>`__)


v0.0.8 (2023-09-21)
===================

Misc
----

- Update dkist-fits-specifications to conform to Revision I of SPEC-0122.


v0.0.7 (2023-09-11)
===================

Bugfixes
--------

- Fixes error in intermediate file mixin log statement. (`#57 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/57>`__)


Misc
----

- Refactor to reduce complexity and hidden mixin->mixin dependency. (`#55 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/55>`__)


v0.0.6 (2023-09-08)
===================

Misc
----

- Use the latest version of dkist-processing-common (4.1.2) to allow the Linearity Correction task to be run on a higher memory worker. (`#60 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/60>`__)


v0.0.5 (2023-09-06)
===================

Misc
----

- Refactor linearity correction to improve memory usage. (`#59 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/59>`__)


v0.0.4 (2023-09-06)
===================

Misc
----

- Update to version 4.1.1 of dkist-processing-common which primarily adds logging and scratch file name uniqueness. (`#58 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/58>`__)


v0.0.3 (2023-08-31)
===================

Misc
----

- Remove parallel computations from the linearity correction task. (`#56 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/56>`__)


v0.0.2 (2023-08-25)
===================

Misc
----

- Change workflow names in documentation builds.


v0.0.1 (2023-08-25)
===================

Misc
----

- Initial release of pipeline for science review
