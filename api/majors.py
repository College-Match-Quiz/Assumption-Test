MAJOR_CIP_CODES = {
    'computer science': {
        '1101', '1107', '1108', '1109', '1110',
    },
    'business': {f'52{code:02d}' for code in range(1, 27)},
    'biology': {f'26{code:02d}' for code in range(1, 13)},
    'engineering': {
        f'14{code:02d}' for code in range(1, 21)
    } | {'1440', '1499'},
    'psychology': {f'42{code:02d}' for code in range(1, 12)},
    'nursing': {
        '5106', '5107', '5108', '5110', '5111', '5112', '5113', '5114',
        '5115', '5116', '5117', '5118', '5119', '5120', '5122', '5123',
        '5124', '5125', '5126', '5127', '5128', '5129',
    },
    'education': {f'13{code:02d}' for code in range(1, 100)},
    'arts': {
        '5007', '5009', '5010', '5012', '5013', '5014', '5015', '5016',
        '5017', '5018', '5019',
    },
    'accounting': {'5203'},
    'anthropology': {'4502'},
    'architecture': {'0402', '0403', '0404', '0408'},
    'chemistry': {'4005', '4006', '4007', '4008', '4009'},
    'communications': {'0901', '0904', '0907', '0909', '1002', '1003'},
    'criminal justice': {f'43{code:02d}' for code in range(1, 10)},
    'economics': {'4506'},
    'english': {f'23{code:02d}' for code in range(1, 10)},
    'environmental science': {'0301', '0302', '0308', '0309', '0401', '0403', '1505'},
    'finance': {'5208'},
    'history': {'5401'},
    'mathematics': {'2701', '2703', '2705', '2706'},
    'marketing': {'5214'},
    'philosophy': {'3801'},
    'physics': {'4008'},
    'political science': {'4510'},
    'public health': {'5102', '5122', '5123'},
    'social work': {'4407'},
    'sociology': {'4511'},
}


def codes_for_majors(majors):
    return {
        major: MAJOR_CIP_CODES.get(major.strip().casefold(), set())
        for major in majors
        if isinstance(major, str) and major.strip()
    }
