# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division

try:
    from oatlib import sensor
except ImportError:
    try:
        import sensor
    except ImportError:
        try:
            from . import sensor
        except ImportError as e:
            raise ImportError("required packages not installed %s" % e)

try:
    from oatlib import oat_utils as ou
except ImportError:
    try:
        import oat_utils as ou
    except ImportError:
        try:
            from . import oat_utils as ou
        except ImportError as e:
            raise ImportError("required packages not installed %s" % e)

# other libs
try:
    import requests
    import pandas as pd
    import isodate
    import datetime
    import warnings
except ImportError as e:
    raise ImportError("required packages not installed %s" % e)

# workaround to remove InsecureRequestWarning from verify=False not checking SSL certificate
requests.packages.urllib3.disable_warnings()


def istSOS2istSOS(
    from_istSOS, to_istSOS, to_sensors, gen_settings={}, verbose=False, minlog=False
):
    """
    Proceed to transfer data from an istSOS instance to another istSOS instance,
    optionally applying data modification according to specifications

        Args:
            from_istSOS (dict): origin istSOS connection configurations - keys are:
                {
                    'service': 'http://istsos.org/istsos/demo',
                    'basic_auth': ('admin', 'admin')
                }'

            to_istSOS (dict): destination istSOS connection configurations - (see from_istsos)

            to_sensors (dict): dict of destination sensor with migration settings - keys are:
                {
                    'A_GNO_GNO': {
                        "urn:ogc:def:parameter:x-istsos:1.0:meteo:air:temperature": {
                            'origin_proc': 'P_TRE',
                            'origin_obspro': 'urn:ogc:def:parameter:x-istsos:1.0:meteo:air:rainfall',
                            'origin_agg_method': 'sum',
                            'origin_agg_freq': 'D',
                            'force_qi': 200, # force aggregated results with this qi
                            'origin_endposition': 'V_TRE' # specify the name of another proc to grasp endposition
                            },
                        "urn:ogc:def:parameter:x-istsos:1.0:meteo:air:rainfall":{
                            'origin_proc': 'T_TRE',
                            'origin_obspro': 'urn:ogc:def:parameter:x-istsos:1.0:meteo:air:temperature',
                            'origin_agg_method': 'mean',
                            'origin_agg_freq': 'D'
                            }
                    },
                    'LOCARNO': {....}
                }
            settings (dict): general settings to be overridden in sensors["MYSENSOR"]["settings"] and
                             in sensors["MYSENSOR"]["MYOBSPROP"]["settings"]

            verbose (bool): print out intermediate steps and results
            minlog (boll): print out minimal information
    """

    # Set default settings
    def_settings = {
        "start_date": "1970-01-01T00:00:00",
        # ↳ start from this date to align periods
        "forcePeriod": [],
        # ↳ force the aggregation in this fixed period
        "updateQualityIndex": True,
        # ↳ update quality index
        "filter_qilist": [],
        # ↳ filter origin data using the qualityIndex in the list
        "min_obs": 1,
        # ↳ set minimum number of observations
        "nan_qi": 0,
        # ↳ set no data quality index
        "nan_data": -999.9,
        #  ↳ set no data value
        "closed": "right",
        #  ↳ use closed right / left intervals
        "label": "right",
        # ↳ set label to right end period
        "tz": "+00:00",
        "full_gap": False,
        # ↳ if force period is not set aggregate all the data gap between origin and dest
        # ↳ end positions completing also missing data
        "data_verbose": False,
        # ↳ print verbose messages
        "test_only": False,
        # ↳ do not actually update data in destination service
        "force_qi": False,
        # ↳ force the quality Index
        "frequency": None,
        # ↳ set frequency to get data from origin
        "forceEndPeriodToOrigin": False,
        # ↳ if force period is set is force the END period to Origin End Position
    }
    forcePeriod = False

    # Set general settings merging general into default
    migrate_settings = def_settings | gen_settings

    # Check origin istsos
    try:
        origin_service = from_istSOS["service"].rstrip("/")
    except:
        raise ValueError("to_istSOS['service'] is mandatory")

    origin_url = "/".join(origin_service.split("/")[:-1])
    origin_instance = origin_service.split("/")[-1]

    if from_istSOS["basic_auth"]:
        if len(from_istSOS["basic_auth"]) == 2:
            origin_auth = from_istSOS["basic_auth"]
        else:
            raise ValueError("<basic_auth> tuple numerosity is TWO")
    else:
        origin_auth = None

    # Check destination istsos
    try:
        destination_service = to_istSOS["service"].rstrip("/")
    except:
        raise ValueError("to_istSOS['service'] is mandatory")

    destination_url = "/".join(destination_service.split("/")[:-1])
    destination_instance = destination_service.split("/")[-1]

    if to_istSOS["basic_auth"]:
        if len(to_istSOS["basic_auth"]) == 2:
            destination_auth = to_istSOS["basic_auth"]
        else:
            raise ValueError("<basic_auth> tuple numerosity is TWO")
    else:
        destination_auth = None

    # set endposition of all observed sensors
    res = requests.get(
        "%s/wa/istsos/services/%s/procedures/operations/getlist"
        % (destination_url, destination_instance),
        auth=destination_auth,
        verify=False,
    )
    data = res.json()
    destination_sensor_lastobs = {}
    destination_sensor_firstobs = {}
    for p in data["data"]:
        if p["samplingTime"]["endposition"]:
            destination_sensor_lastobs[p["name"]] = isodate.parse_datetime(
                p["samplingTime"]["endposition"]
            )
            destination_sensor_firstobs[p["name"]] = isodate.parse_datetime(
                p["samplingTime"]["beginposition"]
            )
        else:
            destination_sensor_lastobs[p["name"]] = isodate.parse_datetime(
                "1700-01-01T00:00:00Z"
            )
            destination_sensor_firstobs[p["name"]] = isodate.parse_datetime(
                "2050-01-01T00:00:00Z"
            )

    # foreach destination sensor
    for dest_sens, obs in list(to_sensors.items()):
        if verbose:
            print("Processing data to update %s procedure" % dest_sens)
        push = True

        # Set sensor settings merging sensor settings into default
        if "settings" in obs:
            sen_settings = migrate_settings | obs["settings"]
        else:
            sen_settings = migrate_settings

        aggsens = {}
        for key, dest_proc in list(obs.items()):
            # Set settings merging specific obspro settings
            if "settings" in dest_proc:
                settings = sen_settings | dest_proc["settings"]
            else:
                settings = sen_settings

            if verbose:
                print("|")
                print(
                    f"|----> aggregating {key.split(':')[-1]} with settings: {settings}"
                )

            # set OAT.sensor from origin
            asen = sensor.Sensor.from_istsos(
                service=origin_service,
                procedure=dest_proc["origin_proc"],
                observed_property=dest_proc["origin_obspro"],
                basic_auth=origin_auth,
            )
            if verbose:
                print("|")
                print("|----> %s oat.sensor created" % key.split(":")[-1])

            timezone = settings["tz"] if "tz" in settings else "Z"

            # first_origin_obs = isodate.parse_datetime(asen.data_availability[0] + timezone)
            # GET ORIGIN ENDPOSITION
            if "origin_endposition" in dest_proc and dest_proc["origin_endposition"]:
                # get end position of origin from other sensor
                other_sen = sensor.Sensor.from_istsos(
                    service=origin_service,
                    procedure=dest_proc["origin_endposition"],
                    observed_property=":",
                    basic_auth=origin_auth,
                )
                last_origin_obs = isodate.parse_datetime(
                    other_sen.data_availability[1] + timezone
                )
                if verbose:
                    print(
                        f"|-----> last_origin_obs from {dest_proc['origin_endposition']}"
                    )
            else:
                last_origin_obs = isodate.parse_datetime(
                    asen.data_availability[1] + timezone
                )

            # GET DESTINATION ENDPOSITION
            last_dest_obs = destination_sensor_lastobs[dest_sens].astimezone(
                ou.Zone(timezone, False, "GMT")
            )
            if verbose:
                print(
                    f"|-----> last_origin_obs/last_dest_obs: {last_origin_obs}/{last_dest_obs}"
                )

            # DEFINE DATA GAP BETWEEN ORIGIN AND DESTINATION TO BE AGGREGATED
            if "forcePeriod" in settings and settings["forcePeriod"]:
                forcePeriod = True
                if len(settings["forcePeriod"].split("/")) == 2:
                    period = settings["forcePeriod"]
                    if verbose:
                        print(
                            f"|-----> forceEndPeriodToOrigin: {settings['forceEndPeriodToOrigin']}"
                        )
                    if (
                        "forceEndPeriodToOrigin" in settings
                        and settings["forceEndPeriodToOrigin"]
                    ):
                        # in this case aggregate only until last_origin_obs
                        force_start = isodate.parse_datetime(
                            settings["forcePeriod"].split("/")[0]
                        )
                        if force_start >= last_origin_obs:
                            warnings.warn(
                                "->ERROR<- forcePeriod start is not lower than last_origin_obs"
                            )
                            continue
                        else:
                            period = f"{force_start.astimezone(ou.Zone(timezone, False, 'GMT')).isoformat()}/{last_origin_obs.astimezone(ou.Zone(timezone, False, 'GMT')).isoformat()}"
                        if verbose:
                            print(f"|-----> forceEndPeriodToOrigin: {period}")
                else:
                    delta = isodate.parse_duration(settings["forcePeriod"])
                    period = "%s/%s" % (
                        (
                            last_dest_obs + datetime.timedelta(milliseconds=2)
                        ).isoformat(),
                        (last_origin_obs - delta).isoformat(),
                    )

            else:
                if last_origin_obs > last_dest_obs:
                    start = isodate.parse_datetime(settings["start_date"] + timezone)
                    if not dest_proc["origin_agg_freq"][0].isdigit():
                        td_freq = pd.to_timedelta(
                            str("1%s" % (dest_proc["origin_agg_freq"]))
                        )
                    else:
                        td_freq = pd.to_timedelta(dest_proc["origin_agg_freq"])
                    gap = int((last_origin_obs - start) / td_freq) * td_freq

                    last_origin_obs = start + gap
                    if verbose:
                        print("|----- start: %s" % start)
                        print("|----- td_freq: %s" % td_freq)
                        print("|----- gap: %s" % gap)
                        print("|----- last_origin_obs: %s" % last_origin_obs)

                    period = "%s/%s" % (
                        last_dest_obs.isoformat(),
                        last_origin_obs.isoformat(),
                    )
                    if verbose:
                        print("|----- period: %s" % period)
                else:
                    if verbose:
                        print(
                            "|----> %s destination end-position > source end-position"
                            % key.split(":")[-1]
                        )
                    push = False
                    break

            # SET FREQUENCY OF AGGREGATION
            if "frequency" in dest_proc and dest_proc["frequency"]:
                frequency = dest_proc["frequency"]
            elif "frequency" in settings:
                frequency = settings["frequency"]
            else:
                frequency = None

            # GET TIME SERIES DATA FROM ORIGIN
            asen.ts_from_istsos(
                service=origin_service,
                procedure=dest_proc["origin_proc"],
                observed_property=dest_proc["origin_obspro"],
                event_time=period,
                freq=frequency,
                basic_auth=origin_auth,
            )
            if verbose:
                print("|----> %s timeSerie uploaded" % key.split(":")[-1])
                if (not asen.ts is None) and (not asen.ts.empty):
                    print("|----> %s origin timeSerie rows" % len(asen.ts))
                else:
                    print("|----> origin timeSerie is Empty")

                if settings["data_verbose"]:
                    if not asen.ts is None:
                        print("|----> STATS")
                        print("|----> %s" % asen.ts.describe())
                        print("|----> DATA")
                        print("|----> %s" % asen.ts)
                    else:
                        print("|----> origin timeSerie is empty")

            ######################################
            # AGGREGATION
            ######################################
            # if an aggregation is required for the specific obsPro
            if "origin_agg_method" in dest_proc and "origin_agg_freq" in dest_proc:
                # if time series exists and is not empty
                if (asen.ts is None) or (asen.ts.empty):
                    if verbose:
                        print(f"|----> %s origin timeSerie is empty")

                if forcePeriod:
                    agg_period = period
                else:
                    agg_period = (
                        f"{last_dest_obs.isoformat()}/{last_origin_obs.isoformat()}"
                        if settings["full_gap"]
                        else None
                    )

                # aggregate based on settings
                aggr = ou.sensorAggergate(
                    asen,
                    aggregation=dest_proc["origin_agg_method"],
                    frequency=dest_proc["origin_agg_freq"],
                    qilist=settings["filter_qilist"]
                    if "filter_qilist" in settings
                    else None,
                    min_obs=settings["min_obs"] if "min_obs" in settings else None,
                    nan_data=settings["nan_data"] if "nan_data" in settings else None,
                    nan_qi=settings["nan_qi"] if "nan_qi" in settings else None,
                    closed=settings["closed"] if "closed" in settings else "right",
                    label=settings["label"] if "label" in settings else "right",
                    period=agg_period,
                )

                # save aggregated data
                aggsens[key] = aggr

                # Verbose output infos
                if settings["data_verbose"]:
                    if settings["full_gap"]:
                        print("|----> AGGREGATING FULL GAP PERIOD")
                        print(f"REINDEXED: {aggsens[key].ts}")
                    else:
                        print("|----> AGGREGATING RECOVERED DATA PERIOD")
                        print(f"DATA: {aggsens[key].ts}")
                if verbose or minlog:
                    print(
                        "|----> %s dest timeSerie aggregated rows"
                        % len(aggsens[key].ts)
                    )

                # if the aggregated series is empty it should be notified and continue
                if (aggsens[key].ts is None) or (aggsens[key].ts.empty):
                    if verbose:
                        print(f"|----> %s destination timeSerie is empty")
                        continue

            # # TODO: se non è nulla la serie va aggregata
            # if (not asen.ts is None) and (not asen.ts.empty):
            #     # TODO: if min_obs == 0 allora aggrego serie con nan_data per tutto il periodo
            #     # if ('min_obs' in settings) and (settings['min_obs'] == 0):
            #     #
            #     # pandas come fare a fare aggregazione su tutto il periodo con freq
            #     # aggregate serie (only if dest_proc['origin_agg_method']
            #     if 'origin_agg_method' in dest_proc and 'origin_agg_freq' in dest_proc:
            #         aggsens[key] = ou.sensorAggergate(
            #                         asen,
            #                         aggregation=dest_proc['origin_agg_method'],
            #                         frequency=dest_proc['origin_agg_freq'],
            #                         qilist=settings['filter_qilist'] if 'filter_qilist' in settings else None,
            #                         min_obs=settings['min_obs'] if 'min_obs' in settings else None,
            #                         closed=settings['closed'] if 'closed' in settings else 'right',
            #                         label=settings['label'] if 'label' in settings else 'right'
            #                     )
            #         if settings['data_verbose']:
            #             print("|----> AGG")
            #             print("|----> %s" % aggsens[key].ts)
            #         if aggsens[key].ts.empty:
            #             push = False
            #         if settings['data_verbose']:
            #             print("|----> %s dest timeSerie aggregated rows" % len(aggsens[key].ts))
            #     else:
            #         aggsens[key] = asen

            #     if 'force_qi' in dest_proc and dest_proc['force_qi']:
            #         aggsens[key].ts['quality'] = dest_proc['force_qi']

            #     # FILL NO DATA WITH PROVIDED VLUES
            #     aggsens[key].ts.fillna(settings['nan_data'])
            #     if verbose:
            #         print("|----> %s timeSerie aggregated" % key.split(":")[-1])
            # # if the origin series is empty
            # elif ('min_obs' in settings) and (settings['min_obs'] == 0):
            #     if verbose:
            #         print("|----> %s timeSerie empty" % key.split(":")[-1])
            #     # DO WE NEED TO AGGREGATE WITH ZEROes or should be forced? this should be from
            #     aindex = pd.date_range(
            #         start=last_dest_obs.isoformat(),
            #         end=last_origin_obs.isoformat(),
            #         freq=dest_proc['origin_agg_freq'],
            #         closed='right')
            #     if len(aindex)>0:
            #         aggsens[key].ts = pd.DataFrame(index=index, columns=['data','quality'])
            #         aggsens[key].ts.fillna(settings['nan_data'])
            #         if verbose:
            #             print(f"|----> filling with {settings['nan_data']} since min_obs is 0")
            # else:
            #     if verbose:
            #         print("|----> %s timeSerie empty" % key.split(":")[-1])
            #     push=False

        # TODO: ends here !!!!!!
        if "force_qi" in settings and settings["force_qi"]:
            aggsens[key].ts["quality"] = dest_proc["force_qi"]

        # insert observations
        if push:
            res = ou.sensors_to_istsos(
                service=destination_service,
                procedure=dest_sens,
                obspro_sensor=aggsens,
                qualityIndex=settings["updateQualityIndex"]
                if "updateQualityIndex" in settings
                else True,
                period=period if forcePeriod else None,
                basic_auth=destination_auth,
                verbose=settings["data_verbose"],
                nan_qi=settings["nan_qi"]
                if "nan_qi" in settings
                else 0,  # TODO: use this for settings or dict in obsepro
                test_only=settings["test_only"] if "test_only" in settings else False,
            )
            if verbose or minlog:
                print("|")
                print("%s procedure successfully updated" % dest_sens)
                print("=================================")
        else:
            if verbose or minlog:
                print("|")
                print("%s procedure not updated" % dest_sens)
                print("=================================")


"""


    sensors = {
                'CANOBBIO': {
                    "urn:ogc:def:parameter:x-istsos:1.0:meteo:air:temperature": {
                        'procedure': 'P_TRE',
                        'obs_pro': 'urn:ogc:def:parameter:x-istsos:1.0:meteo:air:rainfall',
                        'aggregate': 'sum',
                        'frequency': 'D'
                        },
                    "urn:ogc:def:parameter:x-istsos:1.0:meteo:air:rainfall": {
                        'procedure': 'T_TRE',
                        'obs_pro': 'urn:ogc:def:parameter:x-istsos:1.0:meteo:air:temperature',
                        'aggregate': 'mean',
                        'frequency': 'D'
                        }
                },
                {....}
            }

    from_istSOS = {
        'service': 'https://geoservice.ist.supsi.ch/psos/sos',
        'basic_auth': ('admin', 'wP5396Wu7dE6572q')
    }

    to_istSOS = {
        'service': 'http://istsos.org/istsos/demo',
        'basic_auth': ('admin', 'wP5396Wu7dE6572q')
    }

    settings = {
        'forcePeriod': [],
        'updateQualityIndex': True,
        'filter_qilist': [200, 210, 220, 230, 320, 330],
        'min_obs': 1,
        'nan_qi': 100,
        'nan_data': -999.9,
        'closed': 'right',
        'label': 'right',
        'tz': 'Z'
    }
"""
