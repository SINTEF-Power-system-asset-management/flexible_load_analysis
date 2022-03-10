import numpy as np
import matplotlib.pyplot as plt
from utilities import duration_to_hours, datetime_to_season


def remove_unimportant_overloads(l_overloads):
    return list(filter(lambda o: not o.is_unimportant(), l_overloads))

class OverloadEvent:

    # Et ønske at denne klassen ikke bærer med seg for mye, den
    # kan fungere som en naturlig komprimering av datasettet ned i det
    # interessante området.

    def __init__(self, ts_overload_event, fl_power_limit) -> None:
        
        # Time-metrics
        self.dt_start = ts_overload_event[0,0]
        self.dt_end = ts_overload_event[-1,0]
        self.dt_duration = self.dt_end - self.dt_start
        self.duration_h = duration_to_hours(self.dt_duration)

        # Power-metrics
        self.fl_spike = np.max(ts_overload_event[:,1])
        fl_energy = 0
        fl_rms_load = 0
        for i in range(1, len(ts_overload_event)):  # Max Riemann-sum
            fl_max_overload = max(ts_overload_event[i - 1, 1], ts_overload_event[i, 1]) - fl_power_limit
            
            # Can be simplified if hour-requirement is assumed
            dt_dur = (ts_overload_event[i, 0] - ts_overload_event[i - 1, 0])
            fl_dur = duration_to_hours(dt_dur)

            fl_energy += fl_max_overload * fl_dur
            fl_rms_load += ts_overload_event[i - 1, 1] * fl_dur
        self.fl_MWh = fl_energy

        fl_rms_load = fl_rms_load / self.duration_h
        self.fl_rms_load = fl_rms_load
        self.percentage_overload = 100 * fl_rms_load / fl_power_limit
        
        # Insert calculation of ramping here

    def __str__(self):
        return "Overload Event with properties:\n"                                  + \
            "Start              :     " + str(self.dt_start)            + "   \n"      + \
            "End                :     " + str(self.dt_end)              + "   \n"      + \
            "Duration           :     " + str(self.dt_duration)         + "   \n"      + \
            "------------\n"                                                        + \
            "Spike              :     " + str(self.fl_spike)            + "   kW\n"      + \
            "RMS load           :     " + str(self.fl_rms_load)         + "   kW\n"      + \
            "Energy over limit  :     " + str(self.fl_MWh)              + "   kWh\n"      + \
            "% Overload         :     " + str(self.percentage_overload) + "   %\n"


    def is_unimportant(self):
        # Trenger måte å si at en overlasts-hendelse kun var en "liten" overlast
        # Ikke innlysende hvordan dette regnes ut.
        # Denne infoen kan brukes av høyere nivås modul for å fjerne disse
        # hendelsene.
        # Vil være en kombinasjon av varighet, spike, etc.
        dur_hours = duration_to_hours(self.dt_duration)
        if dur_hours == 1:
            b_short = True
        else:
            b_short = False
        return b_short


class FlexibilityNeed:
    # En tidsserie har mange tilfeller av overlast.
    # Flex-behov er en meta-metrikk over disse.

    def __init__(self, l_overloads) -> None:
        self.l_overloads = l_overloads
        self.str_flex_category = "" # Hvilken type overlast ser en oftest?
        # Hvilke andre attributter?

        l_recovery_times = []
        num_overloads = len(l_overloads)
        for i in range(num_overloads):
            if i != num_overloads - 1:  # cannot find recovery-time for last event
                dt_recovery_time = l_overloads[i + 1].dt_start - l_overloads[i].dt_end
                l_recovery_times.append(dt_recovery_time)
        l_recovery_times.append(None)   # Last overload-event has undefined recovery-time
        self.l_recovery_times = l_recovery_times

        self.fl_avg_frequency = np.average([1 / duration_to_hours(t) for t in self.l_recovery_times[:-1]]) # dubius, recheck
        self.fl_avg_spike = np.average([o.fl_spike for o in l_overloads])


# Burde flyttes til analysis?
def find_overloads(ts_data, fl_power_limit):
    l_overloads = []
    b_in_overload_event = False
    for i in range(len(ts_data)):
        b_line_overloaded = (ts_data[i, 1] >= fl_power_limit)
        if b_line_overloaded and not b_in_overload_event:
            b_in_overload_event = True
            i_start = i
        elif not b_line_overloaded and b_in_overload_event:
            i_end = i
            # Velg mellom disse to
            #l_overloads.append(OverloadEvent(ts_data[i_start:i_end,:], fl_power_limit))
            l_overloads.append(OverloadEvent(ts_data[i_start:i_end+1,:], fl_power_limit))
            b_in_overload_event = False
        else:
            continue
    return l_overloads


def plot_flexibility_histograms(flex_need):
    l_overloads = flex_need.l_overloads
    arr_spikes = np.array([o.fl_spike for o in l_overloads])
    arr_energy = np.array([o.fl_MWh for o in l_overloads])
    arr_duration_h = np.array([o.duration_h for o in l_overloads])
    arr_recovery_time_h = np.array([duration_to_hours(t) if t else None for t in flex_need.l_recovery_times])

    fig,axs = plt.subplots(2,2, sharey=True)

    axs[0, 0].hist(arr_spikes, bins='auto')
    axs[0, 0].set_xlabel("Load [kW]")
    axs[0, 0].set_ylabel("Counts")
    axs[0, 0].set_title("Overload-spikes")

    axs[0, 1].hist(arr_energy, bins='auto')
    axs[0, 1].set_xlabel("Energy over limit [kWh]")
    axs[0, 1].set_ylabel("Counts")
    axs[0, 1].set_title("Overload-energy")
    
    axs[1, 0].hist(arr_duration_h, bins='auto')
    axs[1, 0].set_xlabel("Duration [h]")
    axs[1, 0].set_ylabel("Counts")
    axs[1, 0].set_title("Overload-duration")
    
    axs[1, 1].hist(arr_recovery_time_h[:-1], bins='auto')
    axs[1, 1].set_xlabel("Recovery time [h]")
    axs[1, 1].set_ylabel("Counts")
    axs[1, 1].set_title("Recovery time between events")

    plt.tight_layout()

    plt.show()

def plot_flexibility_clustering(flex_need):
    l_overloads = flex_need.l_overloads
    arr_spikes = np.array([o.fl_spike for o in l_overloads])
    arr_energy = np.array([o.fl_MWh for o in l_overloads])
    arr_duration_h = np.array([o.duration_h for o in l_overloads])
    arr_season = np.array([datetime_to_season(o.dt_start) for o in l_overloads])
    arr_month = np.array([o.dt_start.month for o in l_overloads])
    arr_recovery_time_h = np.array([duration_to_hours(t) if t else None for t in flex_need.l_recovery_times])

    fig,axs = plt.subplots(2,2)

    axs[0, 0].scatter(arr_duration_h, arr_spikes)
    axs[0, 0].set_xlabel("Duration [h]")
    axs[0, 0].set_ylabel("Spike [kW]")

    axs[0, 1].scatter(arr_season, arr_spikes)
    axs[0, 1].set_xlabel("Season (1=winter)")
    axs[0, 1].set_ylabel("Spike [kW]")

    axs[1, 0].scatter(arr_season, arr_recovery_time_h)
    axs[1, 0].set_xlabel("Season (1=winter)")
    axs[1, 0].set_ylabel("Recovery time [h]")

    axs[1, 1].scatter(arr_month, arr_spikes)
    axs[1, 1].set_xlabel("Month")
    axs[1, 1].set_ylabel("Spike [kW]")
    
    plt.tight_layout()
    plt.show()