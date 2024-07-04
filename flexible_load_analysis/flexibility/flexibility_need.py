import numpy as np

from .. import utilities as util

def remove_unimportant_overloads(l_overloads):
    return list(filter(lambda o: not o.is_unimportant(), l_overloads))

class OverloadEvent:
    """Storage of metrics associated with a single event of __potentially__ overloaded line

    Attributes:
        dt_start (datetime) : Starting time of event
        dt_end (datetime) : Ending time of event
        duration_h (int) : Duration of event in hours
        fl_spike (float) : Highest observed overload during the event
        fl_surplus_energy_MWh (float) : Total energy above the allowed power limit
        fl_rms_load (float) : RMS power demand during event
        percentage_overload (float) : Percentage of RMS power above limit
        fl_ramping (float) : Approximate ramping speed up to peak overload
    """

    def __init__(
        self,
        ts_overload_event,
        fl_power_limit,
        equal_timestamp_spacing: bool = True,
        widths_for_equally_spaced_timestamps: float | int = 1,
        all_timestamp_widths: list = None,
    ) -> None:
        """Calculate metrics associated with an event

        Args:
            ts_overload_event (timeseries) : Load during event
            fl_power_limit (float) : Power limit of line in question during the event
            equal_timestamp_spacing (bool, optional) : Indicates if timestamps have uniform spacing. Default to True.
            widths_for_equally_spaced_timestamps (float | int, optional) : width for uniformly- spaced timestamps. Default is 1.
            all_timestamp_widths (list, optional) : List of widths for all timestamps in timeseries if they are non-uniformly spaced. Defaults to None.
        """

        # Time-metrics
        self.dt_start = ts_overload_event[0,0]
        self.dt_end = ts_overload_event[-1,0]
        dt_duration = self.dt_end - self.dt_start
        self.duration_h = util.duration_to_hours(dt_duration)

        # Power-metrics
        fl_peak_surplus = np.max(ts_overload_event[:, 1]) - fl_power_limit
        self.fl_spike = max(
            fl_peak_surplus, 0
        )  # Negative overload (surplus capacity) not considered

        fl_energy = 0
        fl_rms_load = 0

        if equal_timestamp_spacing:
            for timestamp, load in ts_overload_event:
                if load > fl_power_limit:
                    fl_energy += (load - fl_power_limit) * widths_for_equally_spaced_timestamps
                fl_rms_load += load * widths_for_equally_spaced_timestamps
                
        else:
            if all_timestamp_widths is None:
                raise ValueError("the list of timestamp widths must be provided when equal_timestamp_spacing is False.")
            for power, width in zip(ts_overload_event[:, 1], all_timestamp_widths):
                if power > fl_power_limit:
                    fl_energy += (power - fl_power_limit)*width
                fl_rms_load += power * width

        self.fl_surplus_energy_MWh = fl_energy
        fl_rms_load = fl_rms_load / self.duration_h
        self.fl_rms_load = fl_rms_load
        self.percentage_overload =(100 * fl_rms_load / fl_power_limit) if fl_power_limit != 0 else -1 

        # TODO: Ramping should really be calculated from the first timestamp before peak where only load increases are observed
        # As in, the power could actually decrease from the time of dt_start, while ramping should be calculated from
        # the first time it only is increasing.
        spike_dur = ts_overload_event[np.argmax(ts_overload_event[:,1]),0] - self.dt_start
        spike_dur_h = util.duration_to_hours(spike_dur)
        self.fl_ramping = (np.max(ts_overload_event[:,1]) - fl_power_limit)/spike_dur_h if spike_dur_h else -1

    def __str__(self):
        return (
            "Overload Event with properties:\n"
            + "Start              :     "
            + str(self.dt_start)
            + "   \n"
            + "End                :     "
            + str(self.dt_end)
            + "   \n"
            + "Duration           :     "
            + str(self.duration_h)
            + "   \n"
            + "------------\n"
            + "Spike over limit   :     "
            + str(self.fl_spike)
            + "   kW\n"
            + "RMS load           :     "
            + str(self.fl_rms_load)
            + "   kW\n"
            + "Energy over limit  :     "
            + str(self.fl_surplus_energy_MWh)
            + "   kWh\n"
            + "% Overload         :     "
            + str(self.percentage_overload)
            + "   %\n"
            + "Ramping            :     "
            + str(self.fl_ramping)
            + "   kW/h\n"
        )

    def is_unimportant(self):
        # TODO: Other ways of characterizing "unimportant load"
        if self.duration_h == 1:
            b_short = True
        else:
            b_short = False
        return b_short


class FlexibilityNeed:
    """
    A timeseries may have many occurences of overloads.
    A flexibility need is defined as a meta-metric over all the overload-events.
    """

    def __init__(self, l_overloads) -> None:
        self.l_overloads = l_overloads
        self.str_flex_category = "" 

        l_recovery_times = []
        num_overloads = len(l_overloads)
        for i in range(num_overloads):
            if i != num_overloads - 1:  # cannot find recovery-time for last event
                dt_recovery_time = l_overloads[i + 1].dt_start - l_overloads[i].dt_end
                l_recovery_times.append(dt_recovery_time)
        l_recovery_times.append(util.undef_timedelta())   # Last overload-event has undefined recovery-time
        self.l_recovery_times = l_recovery_times

        self.fl_avg_frequency = np.average([1 / util.duration_to_hours(t) for t in self.l_recovery_times])
        self.fl_avg_spike = np.average([o.fl_spike for o in l_overloads])

    def extract_arrays(self):
        arrs = {}
        l_overloads = self.l_overloads

        arrs["spike"] = np.array([o.fl_spike for o in l_overloads])
        arrs["energy"] = np.array([o.fl_surplus_energy_MWh for o in l_overloads])
        arrs["duration"] = np.array([o.duration_h for o in l_overloads])
        arrs["season"] = np.array([util.datetime_to_season(o.dt_start) for o in l_overloads])
        arrs["month"] = np.array([o.dt_start.month for o in l_overloads])
        arrs["recovery"] = np.array([util.duration_to_hours(t) for t in self.l_recovery_times])
        arrs["ramping"] = np.array([o.fl_ramping for o in l_overloads])

        return arrs

def metric_annotation(metric_name):
    # TODO: Change to match case when python 3.10 ubiquitous
    ann = ""
    if metric_name == "spike":
        ann = "Spike [kW]"
    elif metric_name == "energy":
        ann = "Energy [kWh]"
    elif metric_name == "duration":
        ann = "Duration [h]"
    elif metric_name == "season":
        ann = "Season"
    elif metric_name == "month":
        ann = "Month"
    elif metric_name == "recovery":
        ann = "Recovery-time [h]"
    elif metric_name == "ramping":
        ann = "Ramping [kW/h]"
    return ann
