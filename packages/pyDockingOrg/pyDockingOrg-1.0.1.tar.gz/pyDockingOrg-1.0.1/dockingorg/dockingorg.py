"""
Based on Python_SmallWorld_API from Matteo Ferla 
(https://python-smallworld-api.readthedocs.io/en/latest/index.html)

Changes:
 - hooks handle events
 - a session is shared for simultaneous requests using threading
"""
import requests
import warnings
from typing import Iterable
import re
import json
import time
from concurrent.futures import ThreadPoolExecutor
from urllib3.util import Retry
from requests.adapters import HTTPAdapter
import atexit

import pandas as pd


class Enamine:

    # Use this Class variable to relay settings for static methods
    _session = None
    RESULTS_PER_SEARCH = 100

    # columns necessary for downloading the data from https://sw.docking.org/search/view
    VALID_COLUMNS = {'columns[0][data]': '0', 'columns[0][name]': 'alignment', 'columns[0][searchable]': 'true',
        'columns[0][orderable]': 'false', 'columns[0][search][value]': '', 'columns[0][search][regex]': 'false',
        'columns[1][data]': '1', 'columns[1][name]': 'dist', 'columns[1][searchable]': 'true',
        'columns[1][orderable]': 'true', 'columns[1][search][value]': '0-12', 'columns[1][search][regex]': 'false',
        'columns[2][data]': '2', 'columns[2][name]': 'ecfp4', 'columns[2][searchable]': 'true',
        'columns[2][orderable]': 'true', 'columns[2][search][value]': '', 'columns[2][search][regex]': 'false',
        'columns[3][data]': '3', 'columns[3][name]': 'daylight', 'columns[3][searchable]': 'true',
        'columns[3][orderable]': 'true', 'columns[3][search][value]': '', 'columns[3][search][regex]': 'false',
        'columns[4][data]': '4', 'columns[4][name]': 'topodist', 'columns[4][searchable]': 'true',
        'columns[4][orderable]': 'true', 'columns[4][search][value]': '0-8', 'columns[4][search][regex]': 'false',
        'columns[5][data]': '5', 'columns[5][name]': 'mces', 'columns[5][searchable]': 'true',
        'columns[5][orderable]': 'true', 'columns[5][search][value]': '', 'columns[5][search][regex]': 'false',
        'columns[6][data]': '6', 'columns[6][name]': 'tdn', 'columns[6][searchable]': 'true',
        'columns[6][orderable]': 'true', 'columns[6][search][value]': '0-6', 'columns[6][search][regex]': 'false',
        'columns[7][data]': '7', 'columns[7][name]': 'tup', 'columns[7][searchable]': 'true',
        'columns[7][orderable]': 'true', 'columns[7][search][value]': '0-6', 'columns[7][search][regex]': 'false',
        'columns[8][data]': '8', 'columns[8][name]': 'rdn', 'columns[8][searchable]': 'true',
        'columns[8][orderable]': 'true', 'columns[8][search][value]': '0-6', 'columns[8][search][regex]': 'false',
        'columns[9][data]': '9', 'columns[9][name]': 'rup', 'columns[9][searchable]': 'true',
        'columns[9][orderable]': 'true', 'columns[9][search][value]': '0-2', 'columns[9][search][regex]': 'false',
        'columns[10][data]': '10', 'columns[10][name]': 'ldn', 'columns[10][searchable]': 'true',
        'columns[10][orderable]': 'true', 'columns[10][search][value]': '0-2', 'columns[10][search][regex]': 'false',
        'columns[11][data]': '11', 'columns[11][name]': 'lup', 'columns[11][searchable]': 'true',
        'columns[11][orderable]': 'true', 'columns[11][search][value]': '0-2', 'columns[11][search][regex]': 'false',
        'columns[12][data]': '12', 'columns[12][name]': 'mut', 'columns[12][searchable]': 'true',
        'columns[12][orderable]': 'true', 'columns[12][search][value]': '', 'columns[12][search][regex]': 'false',
        'columns[13][data]': '13', 'columns[13][name]': 'maj', 'columns[13][searchable]': 'true',
        'columns[13][orderable]': 'true', 'columns[13][search][value]': '0-6', 'columns[13][search][regex]': 'false',
        'columns[14][data]': '14', 'columns[14][name]': 'min', 'columns[14][searchable]': 'true',
        'columns[14][orderable]': 'true', 'columns[14][search][value]': '0-6', 'columns[14][search][regex]': 'false',
        'columns[15][data]': '15', 'columns[15][name]': 'hyb', 'columns[15][searchable]': 'true',
        'columns[15][orderable]': 'true', 'columns[15][search][value]': '0-6', 'columns[15][search][regex]': 'false',
        'columns[16][data]': '16', 'columns[16][name]': 'sub', 'columns[16][searchable]': 'true',
        'columns[16][orderable]': 'true', 'columns[16][search][value]': '0-6', 'columns[16][search][regex]': 'false',
        'order[0][column]': '0', 'order[0][dir]': 'asc',
        'search[value]': '', 'search[regex]': 'false'}

    # extract the column names from the ones we requested
    VALID_COLUMN_NAMES = [v for p, v in VALID_COLUMNS.items() if '[name]' in p]

    # specify the database
    SEARCH_PARAMS = [('db', 'REAL-Database-22Q1.smi.anon'), ('dist', 5), ('tdn', 6), ('rdn', 6), ('rup', 2),
                     ('ldn', 2), ('lup', 2), ('maj', 6), ('min', 6), ('sub', 6), ('sdist', 12), ('tup', 6),
                     ('scores', 'Atom Alignment,ECFP4,Daylight')]

    def __init__(self):
        self._init_session_request()
        atexit.register(self._close_enamine_session)

    @staticmethod
    def _init_session_request():
        Enamine._session = requests.Session()

        # add retries, the server fails sometimes which appears to be internal crashes
        retries = Retry(
            total=3,
            backoff_factor=0.1,
            status_forcelist=[500, 502, 504],
            allowed_methods={'GET'},
        )
        Enamine._session.mount('https://', HTTPAdapter(max_retries=retries))

    def __enter__(self):
        Enamine._init_session_request()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._close_enamine_session()

    def _close_enamine_session(self):
        if Enamine._session is not None:
            Enamine._session.close()

    @staticmethod
    def parse_hitlist_results(response, *args, **kwargs):
        response.enamine_results = pd.DataFrame({})
        try:
            if not response.json()["recordsTotal"]:
                warnings.warn(f'There are {response.json()["recordsTotal"]} hits in the reply')
                return

            reply_data = response.json()['data']
            if not reply_data:
                warnings.warn('There is no `data` in the reply!')
                return
        except requests.exceptions.ChunkedEncodingError:
            pass
        except requests.exceptions.JSONDecodeError as E:
            warnings.warn("Parsing molecules from a hitlist  has failed due to: " + str(E))
            return
        except KeyError as E:
            warnings.warn("Could not access the key: " + str(E))
            return

        # expand the first column
        df1 = pd.DataFrame([row[0] for row in reply_data])
        if len(df1) == 0:
            raise Exception('Reply generated an empty table')
        df2 = pd.DataFrame([row[1:] for row in reply_data], columns=Enamine.VALID_COLUMN_NAMES[1:])

        df = pd.concat([df1, df2], axis=1)
        df['name'] = df.hitSmiles.str.split(expand=True)[1]
        df['smiles'] = df.hitSmiles.str.split(expand=True)[0]
        response.enamine_results = df

    @staticmethod
    def parse_lookup_query(response, *args, **kwargs):
        # set the results to be empty in case something goes wrong
        response.enamine_results = [pd.DataFrame({})]

        hit_list_id = set()
        try:
            for line in response.iter_lines(decode_unicode=True):
                if len(line) == 0:
                    continue

                if type(line) is bytes:
                    continue

                datum = json.loads(re.sub(r'^data:\s?', '', line))
                hit_list_id.add(datum['hlid'])
        except requests.exceptions.ChunkedEncodingError:
            # the server appears to be cutting off the connection after sending the summary
            pass
        except json.decoder.JSONDecodeError:
            # the result cannot be parsed
            return

        if len(hit_list_id) == 0:
            # occasionally the returned results are empty
            return

        for hit_id in hit_list_id:
            params = {"hlid": hit_id, "start": 0, "length": Enamine.RESULTS_PER_SEARCH, "draw": 0}
            params = {**params, **Enamine.VALID_COLUMNS}

            response_molecules: requests.Response = Enamine._session.get(
                url='https://sw.docking.org/search/view',
                params=params,
                stream=True,
                timeout=60,  # seconds
                hooks={"response": Enamine.parse_hitlist_results}
            )

            # return the reply back by attaching it to the response
            response.enamine_results.append(response_molecules.enamine_results)

    @staticmethod
    def parse_lookup_query_v2(response, *args, **kwargs):
        response.enamine_results = pd.DataFrame({})
        try:
            if not response.json()["recordsTotal"]:
                warnings.warn(f'There are {response.json()["recordsTotal"]} hits in the reply')
                return

            reply_data = response.json()['data']
            if not reply_data:
                raise Exception('There is no `data` in the reply!')
        except requests.exceptions.ChunkedEncodingError:
            pass
        except requests.exceptions.JSONDecodeError as E:
            warnings.warn("Parsing molecules from a hitlist  has failed due to: " + str(E))
            return
        except KeyError as E:
            warnings.warn("Could not access the key: " + str(E))
            return

        # expand the first column
        df1 = pd.DataFrame([row[0] for row in reply_data])
        if len(df1) == 0:
            raise Exception('Reply generated an empty table')
        # I don't know what the columns represent in the new interface, but these columns are not used for now
        df2 = pd.DataFrame([row[1:] for row in reply_data], columns=["qrySmiles", "fp", "similarity", "c1", "c2", "c3", "c4", "c5"])

        df = pd.concat([df1, df2], axis=1)
        df['name'] = df.hitSmiles.str.split(expand=True)[1]
        df['smiles'] = df.hitSmiles.str.split(expand=True)[0]
        response.enamine_results = df

    @staticmethod
    def get_molecules_v2(smiles):
        reply: requests.Response = Enamine._session.get(
            url='https://sw.docking.org/search/view',
                params=[('db', 'REAL-Database-22Q1.smi.anon'),
                        ('dist', 5),
                        ('tdn', 6),
                        ('rdn', 6),
                        ('rup', 2),
                        ('ldn', 2),
                        ('lup', 2),
                        ('maj', 6),
                        ('min', 6),
                        ('sub', 6),
                        ('sdist', 12),
                        ('tup', 6),
                        ('fmt', 'json'),
                        ('scores', 'Atom Alignment,ECFP4,Daylight')
                        ]
                       +
                       [('smi', smi) for smi in smiles],
            stream=True,
            timeout=60,  # seconds
            hooks={'response': Enamine.parse_lookup_query_v2}
            )
        return reply.enamine_results

    @staticmethod
    def get_molecules(smiles):
        reply: requests.Response = Enamine._session.get(
            url='https://sw.docking.org/search/submit',
                params=Enamine.SEARCH_PARAMS +  [('smi', smiles)],
            stream=True,
            timeout=60,  # seconds
            hooks={'response': Enamine.parse_lookup_query}
            )
        return pd.concat(reply.enamine_results)

    @staticmethod
    def get_molecules_batch(smiles):
        reply: requests.Response = Enamine._session.get(
            url='https://sw.docking.org/search/submit',
                params=Enamine.SEARCH_PARAMS +  [('smi', smi) for smi in smiles],
            stream=True,
            timeout=60,  # seconds
            hooks={'response': Enamine.parse_lookup_query}
            )
        return pd.concat(reply.enamine_results)

    def close(self):
        Enamine._session.close()

    def search_smiles_v2(self, smiles: Iterable[str], remove_duplicates=False, max_workers=5):
        """
        Search
        Args:
            smiles: a bag of smiles that you'd like to search for
            remove_duplicates: ensure the found Smiles are unique. If the same Smiles were found with different query smiles,
                remove the duplicates. This means you will not be able to recover which Smiles led to

        Returns:

        """
        start = time.time()

        # batch smiles together and query the server 20 miles per call
        from more_itertools import chunked

        dfs = [Enamine.get_molecules_v2(batch) for batch in chunked(smiles, 20)]

        mols = pd.concat(dfs)

        if remove_duplicates:
            mols.drop_duplicates(subset='id', inplace=True)

        print(f"Found {len(mols)} in {time.time() - start}")
        return mols

    def search_smiles(self, smiles: Iterable[str], remove_duplicates=False, max_workers=1):
        """
        Search
        Args:
            smiles: a list of smiles that you'd like to search for
            remove_duplicates: ensure the found Smiles are unique. If the same Smiles were found with different query smiles,
                remove the duplicates. This means you will not be able to recover which Smiles led to

        Returns:
        """

        if type(smiles) is str:
            smiles = [smiles]

        # set this to be used later in the calls
        Enamine.RESULTS_PER_SEARCH = 100

        start = time.time()
        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            dfs = list(pool.map(Enamine.get_molecules, smiles))

        mols = pd.concat(dfs)

        if remove_duplicates:
            mols.drop_duplicates(subset='id', inplace=True)

        print(f"Found {len(mols)} in {time.time() - start}")
        return mols

    def search_smiles_batch(self, smiles: Iterable[str], remove_duplicates=False, max_workers=5):
        """
        Search
        Args:
            smiles: a bag of smiles that you'd like to search for
            remove_duplicates: ensure the found Smiles are unique. If the same Smiles were found with different query smiles,
                remove the duplicates. This means you will not be able to recover which Smiles led to

        Returns:

        """
        # for each smile search take 100 smiles
        Enamine.RESULTS_PER_SEARCH = 20_000

        start = time.time()

        # batch smiles together and query the server 20 miles per call
        from more_itertools import chunked

        dfs = [Enamine.get_molecules(batch) for batch in chunked(smiles, 20)]

        mols = pd.concat(dfs)

        if remove_duplicates:
            mols.drop_duplicates(subset='id', inplace=True)

        print(f"Found {len(mols)} in {time.time() - start}")
        return mols



def test_duplicates():
    enamine = Enamine()

    # note the duplicate query Smiles
    smiles_to_search = ['O=C(C)Oc1ccccc1C(=O)O', 'C=C(Cl)CNC(=O)C1(CC)CCC1', 'C=C(Cl)CNC(=O)C1(CC)CCC1']
    mols = enamine.search_smiles(smiles_to_search, remove_duplicates=True)

    assert len(mols) <= 230 # assumes 100 results per search, the extra 30 is for the randomness

    print(mols)

    enamine.close()

if __name__ == '__main__':
    # test_duplicates()

    with Enamine() as enamine:
        mols = enamine.search_smiles(
            ['O=C(C)Oc1ccccc1C(=O)O', 'C=C(Cl)CNC(=O)C1(CC)CCC1'], 
            remove_duplicates=True)
        print(mols)
