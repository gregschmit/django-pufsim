from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models, transaction
from gfklookupwidget.fields import GfkLookupField
import math
import numpy as np
import os
import puflib as pl
import subprocess
import sys


from pufsim.models import PUFGenerator


def find_in_path(filename):
    """
    Resolve filename to full path; needed for Apache.
    """
    try:
        ospath = os.environ['PATH']
        ospath = ospath.split(os.pathsep)
    except KeyError:
        ospath = []
    for p in list(sys.path) + ospath + ['/usr/local/bin']:
        try:
            for f in os.listdir(p):
                if filename == f: return os.path.join(p, f)
        except (FileNotFoundError, NotADirectoryError):
            pass
    return None


class ModelAnalyzer(models.Model):
    name = models.CharField(max_length=255)
    progress = models.IntegerField(default=0, editable=False)
    data = models.TextField(blank=True, editable=False)
    pid = models.IntegerField(default=0, editable=False)

    class Meta:
        abstract = True

    def get_operations(self):
        """
        Return a list of tuples of currently possible operations.
        """
        ops = []
        if not self.pid: ops.append('Run')
        if self.data and not self.pid: ops.append('ShowData')
        return ops

    @classmethod
    def get_all_operations(cls):
        return ['Run', 'ShowData']

    @classmethod
    def check_pids(cls):
        objs = cls.objects.all()
        for obj in objs:
            obj.check_pid()

    def check_pid(self):
        if not self.pid: return
        e = True
        try: os.kill(self.pid, 0)
        except OSError: e = False
        if not e:
            self.pid = 0
            self.save()

    @transaction.atomic
    def spawn(self):
        obj = type(self).objects.select_for_update().get(id=self.id)
        args = ['run_analyzer', type(self).__name__, str(self.id)]
        py3 = find_in_path('python3')
        py = find_in_path('python')
        if not py3: py3 = 'python3'
        if not py: py = 'python'
        manage = find_in_path('manage.py')
        if not manage: manage = 'manage.py'
        cmd1 = ' '.join([py3, manage, *args])
        cmd2 = ' '.join([py, manage, *args])
        try: p = subprocess.Popen(cmd1, shell=True)
        except: p = subprocess.Popen(cmd2, shell=True)
        obj.pid = p.pid
        obj.save()
        return p

    def run(self):
        """
        Run the analyzer and store the data.
        """
        raise NotImplementedError

    def get_data_display(self, graph_top=100):
        """
        Return a dictionary so the admin engine can render the data.

        Return Dictionary:
         - type: The type of view that should render the data (valid values:
            'message', 'bar_graph')
         - data: The object's ``data`` attribute
        """
        try:
            value = int(self.data)
            msg = '{} {} returned {}, or %{}'
            percent = 100 * value / self.number_of_pufs
            cls = self.__class__.__name__
            return {
                'type': 'message',
                'msg': msg.format(cls, str(self), value, percent),
            }
        except ValueError:
            return {
                'type': 'bar_graph',
                'data': self.data,
                'graph_top': graph_top,
            }


class BitflipAnalyzer(ModelAnalyzer):
    """
    Build many PUFs and test challenges which differ from the base by a single
    bit being flipped
    """
    puf_generator = models.ForeignKey(PUFGenerator, verbose_name='PUF generator', on_delete=models.CASCADE)
    base_challenge = models.IntegerField(default=0, help_text="Enter the challenge as a decimal value and the system will truncate or add zeros to the most significant bit side (e.g., 12 will be converted to 1100 and then padded to 001100 if the PUF has 6 stages)")
    number_of_pufs = models.IntegerField(default=100)

    model_order = 1

    class Meta:
        verbose_name = 'Bitflip Analyzer'

    def __str__(self):
        return self.name

    def run(self):
        """
        Build pufs, process them while updating progress, return data.
        """
        data = {k: v for (k, v) in [(x, 0) for x in range(self.puf_generator.stages)]}
        for i in range(self.number_of_pufs):
            self.progress = int(i*100 / self.number_of_pufs)
            self.save()
            p = self.puf_generator.generate_puf()
            for j in range(len(p.stages)):
                c = p.get_bitstring(self.base_challenge)
                # flip j'th bit
                c_prime = c[:len(c)-j-1] + ('0' if c[len(c)-j-1] == '1' else '1') + c[len(c)-j:]
                t1 = p.run(c)
                t2 = p.run(c_prime)
                if t1 != t2: data[j] += 1
        self.progress = 100
        self.data = data
        self.save()
        return data

    def get_data_display(self, graph_top=100):
        return super().get_data_display(graph_top=self.number_of_pufs)


class ChallengePairAnalyzer(ModelAnalyzer):
    """
    Build many PUFs and examine the response of two challenges
    """
    puf_generator = models.ForeignKey(PUFGenerator, on_delete=models.CASCADE)
    base_challenge = models.IntegerField(default=0, help_text="Enter the challenge as a decimal value and the system will truncate or add zeros to the most significant bit side (e.g., 12 will be converted to 1100 and then padded to 001100 if the PUF has 6 stages)")
    test_challenge = models.IntegerField(default=0, help_text="Enter the challenge as a decimal value and the system will truncate or add zeros to the most significant bit side (e.g., 12 will be converted to 1100 and then padded to 001100 if the PUF has 6 stages)")
    number_of_pufs = models.IntegerField(default=100)

    model_order = 2

    class Meta:
        verbose_name = 'Challenge Pair Analyzer'

    def __str__(self):
        return self.name

    def run(self):
        """
        Build pufs, process them while updating progress, return data.
        """
        data = 0
        for i in range(self.number_of_pufs):
            print('doing {}'.format(i))
            self.progress = int(i*100 / self.number_of_pufs)
            self.save()
            p = self.puf_generator.generate_puf()
            c = p.get_bitstring(self.base_challenge)
            c_prime = p.get_bitstring(self.test_challenge)
            t1 = p.run(c)
            t2 = p.run(c_prime)
            if t1 != t2: data += 1
        self.progress = 100
        self.data = data
        self.save()
        return data


class NeighborPredictor(ModelAnalyzer):
    """
    Sample many PUFs multiple times and select k-closest neighbors to predict
    the outcome (simple average of k-closest)
    """
    puf_generator = models.ForeignKey(PUFGenerator, on_delete=models.CASCADE)
    distance_choices = [
        ('gamma', 'gamma'),
        ('hamming', 'hamming'),
    ]
    k = models.IntegerField(default=1, help_text="0 for choose all")
    distance = models.TextField(default='gamma', max_length=30, choices=distance_choices)
    known_set_limit = models.IntegerField(default=2, help_text="The predictor will iterate over `n` from `k` to `known_set_limit`, where `n` is the known set size that we use to predict the next challenge.")
    number_of_pufs = models.IntegerField(default=100)
    iterations_per_puf = models.IntegerField(default=100)
    hop_by_power_of_two = models.BooleanField(default=False, help_text="Bins go from K to known_set_limit, if this option is checked, then go from 2^(K-1) to 2^(known_set_limit).")

    model_order = 3

    class Meta:
        verbose_name = 'Neighbor Predictor'

    def __str__(self):
        return self.name

    def run(self):
        """
        Build pufs, process them while updating progress, return data.
        """
        if self.hop_by_power_of_two:
            data = dict([(2**x, 0) for x in range(self.k, self.known_set_limit+1)])
        else:
            #data = [0 for x in range(self.known_set_limit+1)]
            data = dict([(x, 0) for x in range(self.k, self.known_set_limit+1)])
        for i in range(self.number_of_pufs):
            self.progress = int(i*100 / self.number_of_pufs)
            self.save()
            p = self.puf_generator.generate_puf()
            for k, bin in data.items():
                # randomly generate k crps
                crps = p.generate_random_crps(k)
                for iter in range(self.iterations_per_puf):
                    # randomly generate challenge
                    ch = pl.generate_random_challenges(1, self.puf_generator.stages)[0]
                    # order the set of CRPs
                    ordered = [] # tuples of (distance, c, r)
                    for (c, r) in crps:
                        if self.distance == 'gamma':
                            #ordered.append((pl.gamma(c, ch), c, r))
                            ordered.append({'distance': pl.gamma(c, ch), 'challenge': c, 'response': r})
                        else:
                            #ordered.append((pl.hamming(c, ch), c, r))
                            ordered.append({'distance': pl.hamming(c, ch), 'challenge': c, 'response': r})
                    ordered.sort(key=lambda dict: abs(dict['distance']), reverse=True)
                    # average k of them
                    match_total = 0
                    match_sum = 0
                    r = self.k or k
                    for n in range(r):
                        match_total += 1
                        bet = ordered[n]['response']
                        if ordered[n]['distance'] < 0:
                            bet = 0 if bet else 1
                        match_sum += bet
                    # average them and round
                    try:
                        prediction = match_sum / match_total
                        prediction = 1 if prediction >= 0.5 else 0
                    except ZeroDivisionError:
                        prediction = np.random.choice([0, 1])
                    # add to histogram if we successfully predicted the result
                    true = p.run(ch)
                    if prediction == true: data[k] += 1
        self.progress = 100
        for k, bin in data.items():
            data[k] = 100*bin/(self.number_of_pufs*self.iterations_per_puf)
        self.data = data
        self.save()
        return data


class BiasTester(ModelAnalyzer):
    """
    Take sample challenges and find how what proportion of the responses are 1
    """
    puf_type_limit = models.Q(app_label = 'pufsim', model = 'pufgenerator') | models.Q(app_label = 'pufsim', model = 'compositepufgenerator')
    puf_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to=puf_type_limit)
    puf_id = GfkLookupField('puf_type')
    puf_generator = GenericForeignKey('puf_type', 'puf_id')
    number_of_pufs = models.IntegerField(default=100)
    n = models.IntegerField(default=100, help_text='How many samples to get for each PUF')

    model_order = 4

    class Meta:
        verbose_name = 'Bias Tester'

    def __str__(self):
        return self.name

    def run(self):
        """
        Build pufs, process them while updating progress, return data.
        """
        data = dict([(x, 0) for x in range(self.number_of_pufs)])
        for i in range(self.number_of_pufs):
            p = self.puf_generator.generate_puf()
            c = pl.generate_random_challenges(self.n, self.puf_generator.stages)
            current = 0
            for j in range(len(c)):
                self.progress = int(100*(1+j+i*self.n)/(self.number_of_pufs * self.n))
                self.save()
                if p.run(c[j]):
                    current += 1
            data[i] = 100*current / self.n
        self.progress = 100
        dataset = list(data.values())
        data['meta'] = {}
        data['meta']['mean_deviation'] = self.mean_deviation(dataset)
        data['meta']['variance'] = self.variance(dataset)
        self.data = data
        self.save()
        return data

    def mean_deviation(self, dataset):
        a = sum(dataset) / len(dataset)
        return sum([abs(x-a) for x in dataset]) / len(dataset)

    def variance(self, dataset):
        a = sum(dataset) / len(dataset)
        return sum([(x-a)**2 for x in dataset]) / len(dataset)
