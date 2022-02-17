import numpy as np


class FlexibilityNeed:

    # Et ønske at denne klassen ikke bærer med seg for mye, den
    # kan fungere som en naturlig komprimering av datasettet ned i det
    # interessante området.

    def __init__(self, ts_overload_event, fl_power_limit) -> None:
        
        # Time-metrics
        self.dt_start = ts_overload_event[0,0]
        self.dt_end = ts_overload_event[-1,0]
        self.dt_duration = self.dt_end - self.dt_start

        # Power-metrics
        self.fl_spike = np.max(ts_overload_event[:,1])
        fl_energy = 0
        for i in range(1, len(ts_overload_event)):  # Max Riemann-sum
            fl_val = max(ts_overload_event[i - 1, 1], ts_overload_event[i, 1])
            # Can be simplified if hour-requirement is assumed
            dt_dur = (ts_overload_event[i, 0] - ts_overload_event[i - 1, 0])
            fl_dur = dt_dur.seconds / 3600 + dt_dur.days * 24

            fl_energy += fl_val * fl_dur
        self.fl_MWh = fl_energy

    def __str__(self):
        return "Flexibility need with properties:\n"                    + \
            "Start      :     " + str(self.dt_start)        + "\n"      + \
            "End        :     " + str(self.dt_end)          + "\n"      + \
            "Duration   :     " + str(self.dt_duration)     + "\n"      + \
            "------------\n"                                            + \
            "Spike      :     " + str(self.fl_spike)        + "\n"      + \
            "Energy     :     " + str(self.fl_MWh)          + "\n"      + \
            "-------------------------------------------------------------\n"


    def is_unimportant(self):
        # Trenger måte å si at en overlasts-hendelse kun var en "liten" overlast
        # Ikke innlysende hvordan dette regnes ut.
        # Denne infoen kan brukes av høyere nivås modul for å fjerne disse
        # hendelsene.
        pass
        

def detect_flexibility_need(ts_data, fl_power_limit):
    flex_needs = []
    b_in_overload_event = False
    for i in range(len(ts_data)):
        b_line_overloaded = (ts_data[i, 1] >= fl_power_limit)
        if b_line_overloaded and not b_in_overload_event:
            b_in_overload_event = True
            i_start = i
        elif not b_line_overloaded and b_in_overload_event:
            i_end = i
            #if i_end - i_start == 1: print("Flex-event of duration 1")
            flex_needs.append(FlexibilityNeed(ts_data[i_start:i_end+1,:], fl_power_limit))
            b_in_overload_event = False
        else:
            continue
    return flex_needs

