from typing import Union

import pandas as pd

from strideutils import stride_requests
from strideutils.stride_config import config


def check_slack_on_mainnet(str_output: bool = True, verbose: bool = False) -> Union[pd.DataFrame, str]:
    '''
    Outputs a dataframe describing how much slack there is on the redemption rate bounds on mainnet

    if str_output=True, this outputs the output as a pretty string instead of a DF
    '''
    df = []
    output = ""
    for zone in config.host_zones:
        host_zone_id = zone.id
        host_zone = stride_requests.get_host_zone_json(host_zone_id)

        rr = host_zone['redemption_rate']
        min_rr, max_rr = host_zone['min_redemption_rate'], host_zone['max_redemption_rate']
        inner_min_rr, inner_max_rr = host_zone['min_inner_redemption_rate'], host_zone['max_inner_redemption_rate']

        tighter_bound_min = max(min_rr, inner_min_rr)
        tigher_bound_max = min(max_rr, inner_max_rr)

        down_slack = (rr - tighter_bound_min) * 100 * 100 / rr
        up_slack = (tigher_bound_max - rr) * 100 * 100 / rr

        halted = host_zone['halted']

        df.append(
            {'host_zone_id': host_zone_id, 'rr': rr, 'down_slack': down_slack, 'up_slack': up_slack, 'halted': halted}
        )

    df: pd.DataFrame = pd.DataFrame(df).set_index('host_zone_id')
    if str_output or verbose:
        for i, r in df.iterrows():
            output += '{:<16}\tRR: {:.6f}\tDown Slack: {:.2f}bps\tUp Slack: {:.2f}bps\n'.format(
                i, r['rr'], r['down_slack'], r['up_slack']
            )

    if verbose:
        print(output)

    if str_output:
        return output

    return df
