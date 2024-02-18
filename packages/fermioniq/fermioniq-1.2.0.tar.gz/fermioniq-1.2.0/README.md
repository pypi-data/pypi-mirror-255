<!-- ![Fermioniq](https://docs.fermioniq.com/_static/light_logo_trans.svg "Fermioniq") -->
<h1 align="center">
<img src="https://docs.fermioniq.com/_static/light_logo_trans_pad_top.svg" width="500">
</h1><br>

This package is the interface to the Fermioniq quantum circuit emulator.
The client can be used to send jobs, monitor their status and receive results.


- Website: [fermioniq.com](https://www.fermioniq.com)
- Documentation: [docs.fermioniq.com](https://docs.fermioniq.com)


## Prerequisites

Before installing the package, ensure you have met the following requirements:

* You have a working installation of Python (3.10)
* You have installed the `pip` package manager


## Installation

You can install the client with the following command:

```console
pip install fermioniq
```


## Setup:

Sending jobs to the emulator requires a user-specific `access_token_id` and `access_token_secret`.
They are tied to your Fermioniq user account.

You can either define them as environment variables

    - export FERMIONIQ_ACCESS_TOKEN_ID=""
    - export FERMIONIQ_ACCESS_TOKEN_SECRET=""

Alternatively, you can also provide them as input arguments to the `fermioniq.Client` constructor.
