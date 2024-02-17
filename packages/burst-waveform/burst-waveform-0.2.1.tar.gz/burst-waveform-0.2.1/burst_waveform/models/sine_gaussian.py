import numpy as np
from gwpy.timeseries import TimeSeries


class SineGaussian:
    def __init__(self, parameters):
        """
        Initialize class. The ``parameters`` dictionary can
        contain the following:

        Parameters
        ----------
        waveform_dict: dict
            Dictionary containing waveform parameters
        model: str
            Name of waveform model
        """
        self.params = self._validate_params(parameters)

    @staticmethod
    def _validate_params(parameters):
        default_params = {
            "amplitude": 1.0,
            "frequency": 100.0,
            "duration": None,
            "delay": 0.0,
            "sample_rate": 16384.0,
        }

        waveform_params = parameters.copy()
        for key in default_params:
            if key not in parameters:
                waveform_params[key] = default_params[key]

        if waveform_params["duration"] is None:
            raise ValueError("Duration is not specified")

        return waveform_params

    def __call__(self):
        return self._evaluate_model()

    def _evaluate_model(self):
        sample_rate = self.params["sample_rate"]
        delay = self.params["delay"]
        duration = self.params["duration"]
        frequency = self.params["frequency"]

        m = int(6*duration*sample_rate)
        if m > int(sample_rate)/2-1:
            m = int(sample_rate)/2-2

        t = np.arange(0, m, 1)/sample_rate
        g = 2*np.exp(-t*t/2/duration/duration)*np.sin(2*np.pi*frequency*t)
        sum = np.sum(g*g)

        amplitude = self.params["amplitude"]*np.sqrt(sample_rate/sum)

        t = np.arange(1, m, 1)/sample_rate
        g = amplitude*np.exp(-t*t/2/duration/duration)*np.sin(2*np.pi*frequency*t)

        waveform = np.concatenate((-g[::-1], np.zeros(1), g))
        # t = np.concatenate((-t[::-1], np.zeros(1), t))

        timeseries = TimeSeries(waveform, t0=-t[-1], sample_rate=sample_rate, name='sine_gaussian')

        return timeseries


class SineGaussianQ(SineGaussian):
    def __init__(self, parameters):
        """
        Initialize class. The ``parameters`` dictionary can
        contain the following:

        Parameters
        ----------
        waveform_dict: dict
            Dictionary containing waveform parameters
        model: str
            Name of waveform model
        """
        parameters = self._validate_params_SGQ(parameters)
        super(SineGaussianQ, self).__init__(parameters)

    @staticmethod
    def _validate_params_SGQ(parameters):
        default_params = {
            "amplitude": 1.0,
            "frequency": None,
            "Q": None,
        }

        waveform_params = parameters.copy()
        for key in default_params:
            if key not in parameters:
                waveform_params[key] = default_params[key]

        if waveform_params["frequency"] is None:
            raise ValueError("Frequency is not specified")

        if waveform_params["Q"] is None:
            raise ValueError("Q is not specified")

        waveform_params["duration"] = waveform_params["Q"] / (np.pi * 2 * waveform_params["frequency"])

        return waveform_params