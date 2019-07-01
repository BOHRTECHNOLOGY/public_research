"""An example on how to use QBSolv with wrapped sampler."""
from itertools import product
import numpy as np
from dwave_qbsolv import QBSolv
from dwave.system.samplers import DWaveSampler
from dwave.system.composites import EmbeddingComposite
from sampler_recorder import record_sampler_invocations

ENDPOINT = 'https://cloud.dwavesys.com/sapi'
def main():
    """Entrypoint of this script.

    Synopsis is as follows:
      - construct qubo of some predefined size
      - solve it using QBSolv with patched sampler
      - show what is recorded
    """
    with open('dwave_credentials.txt') as token_file:
        token = token_file.read()

    qubo_dict = get_random_qubo(50)
    sampler = EmbeddingComposite(DWaveSampler(token=token, endpoint=ENDPOINT))

    with record_sampler_invocations(sampler) as records:
        response = QBSolv().sample_qubo(qubo_dict, solver_limit=30, solver=sampler)

    print('Sampler was invoked this many times: {}'.format(len(records)))

    # In this example we take only qubo calls - when I tested it it were the only
    # ones made
    qubo_timings = [record['timing'] for record in records if record['method'] == 'qubo']
    total_sampling_time = sum(record['qpu_sampling_time'] for record in qubo_timings)
    print('Average QPU samping time [QUBO]: {}'.format(total_sampling_time / len(qubo_timings)))


def get_random_qubo(size):
    return {(i, j): np.random.rand() for i, j in product(range(size), range(size))}


if __name__ == '__main__':
    main()
