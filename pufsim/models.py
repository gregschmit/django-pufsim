from django.db import models, transaction
import math
import numpy as np
import os
import puflib as pl
import subprocess
import sys


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


class ModelEnv(models.Model):
    class Meta:
        abstract = True

    @classmethod
    def get_display_fields(cls):
        r = []
        for f in cls._meta.get_fields():
            if f.editable:
                r.append(f)
        return r

    @classmethod
    def get_edit_fields(cls):
        return [x for x in cls.get_display_fields() if x.name != 'id']

    @classmethod
    def get_uri_name(cls):
        return cls._meta.verbose_name_plural.lower().replace(' ', '_')


class ModelAnalyzer(models.Model):
    progress = models.IntegerField(default=0, editable=False)
    data = models.TextField(blank=True, editable=False)
    pid = models.IntegerField(default=0, editable=False)

    class Meta:
        abstract = True

    @classmethod
    def get_uri_name(cls):
        return cls._meta.verbose_name_plural.lower().replace(' ', '_')

    @classmethod
    def get_display_fields(cls):
        r = []
        p = []
        for f in cls._meta.get_fields():
            if f.editable or f.name == 'pid' or f.name == 'progress':
                if f.name == 'progress' or f.name == 'pid':
                    p.append(f)
                else:
                    r.append(f)
        return r + p

    @classmethod
    def get_edit_fields(cls):
        return [x for x in cls.get_display_fields() if x.name not in ['id', 'pid', 'progress']]

    def get_actions(self):
        """
        Return a list of tuples of possible actions.
        """
        a = []
        if not self.pid: a.append('run')
        if self.data and not self.pid: a.append('show')
        return a

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


class PDF(ModelEnv):
    """
    Represents a probability distribution function; principle method is
    `get_rng` which will generate random numbers according to the PDF.
    """
    distys = [
        ('dirac', 'dirac delta (singleton)'),
        ('normal', 'normal (gaussian)'),
        ('uniform', 'uniform'),
    ]
    distribution = models.CharField(max_length=30, choices=distys)
    mean = models.FloatField(default=10.0, blank=True, null=True)
    sigma = models.FloatField(default=0.1, blank=True, null=True)
    lbound = models.FloatField(default=9.9, blank=True, null=True)
    rbound = models.FloatField(default=10.1, blank=True, null=True)

    class Meta:
        verbose_name = 'Probability Distribution Function'

    def get_actions(self): return None

    @property
    def opt_fields(self):
        if self.distribution == 'dirac':
            return ['mean',]
        if self.distribution == 'normal':
            return ['mean', 'sigma',]
        if self.distribution == 'uniform':
            return ['lbound', 'rbound',]
        return None

    @property
    def nopt_fields(self):
        r = ['mean', 'sigma', 'lbound', 'rbound']
        for e in self.opt_fields:
            try: r.remove(e)
            except ValueError: pass
        return r

    def save(self, *args, **kwargs):
        for x in self.opt_fields:
            if getattr(self, x) is None: setattr(self, x, 0.0)
        for x in self.nopt_fields:
            setattr(self, x, None)
        return super().save(*args, **kwargs)

    def __str__(self):
        return '{0}({1})'.format(
            self.distribution,
            ', '.join(
                ['{0}={1}'.format(x, str(getattr(self, x, None))) for x in self.opt_fields]
            )
        )

    def get_rng(self):
        if self.distribution == 'dirac':
            return lambda: self.mean
        if self.distribution == 'normal':
            return lambda: np.random.normal(self.mean, self.sigma)
        if self.distribution == 'uniform':
            return lambda: np.random.uniform(self.lbound, self.rbound)
        return None


class PUFGenerator(ModelEnv):
    """
    Model for building delay-based PUFs.
    """
    archs = [
        ('loop', 'loop'),
        ('arbiter', 'arbiter'),
    ]
    architecture = models.CharField(max_length=30, choices=archs)
    stages = models.IntegerField(default=10)
    production_pdf = models.ForeignKey(PDF, on_delete=models.CASCADE)
    sample_pdf = models.ForeignKey(PDF, on_delete=models.CASCADE, related_name='sample_pdf_revacc')
    sensitivity = models.FloatField(default=0.0)

    class Meta:
        verbose_name = 'PUF Generator'

    def __str__(self):
        return "PUFGenerator-{0}[stages={1}, production_pdf={2}, sample_pdf={3}]".format(self.architecture, self.stages, self.production_pdf, self.sample_pdf)

    def get_actions(self):
        return ['quicktest']

    def generate_puf(self):
        """
        Generate a PUF based on the specifications.
        """
        p = self.production_pdf.get_rng()
        s = self.sample_pdf.get_rng()
        if self.architecture == 'loop':
            return pl.Loop(self.stages, self.sensitivity, p, s)
        if self.architecture == 'arbiter':
            return pl.Arbiter(self.stages, self.sensitivity, p, s)
        return None


class BitflipAnalyzer(ModelAnalyzer):
    """
    Build many PUFs and test challenges with bitflips to examine how often the
    response changes.
    """
    puf_generator = models.ForeignKey(PUFGenerator, on_delete=models.CASCADE)
    base_challenge = models.IntegerField(default=0, help_text="Enter the challenge as a decimal value and the system will truncate or add zeros to the most significant bit side (e.g., 12 will be converted to 1100 and then padded to 001100 if the PUF has 6 stages)")
    number_of_pufs = models.IntegerField(default=100)

    class Meta:
        verbose_name = 'Bitflip Analyzer'

    def __str__(self):
        return "BitflipAnalyzer[{0}, base_challenge={1}, n_pufs={2}]".format(self.puf_generator, self.base_challenge, self.number_of_pufs)

    def run(self):
        """
        Build pufs, process them while updating progress, return data.
        """
        data = [0 for x in range(self.puf_generator.stages)]
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


class ChallengePairAnalyzer(ModelAnalyzer):
    """
    Build many PUFs and test two challenges and how they affect the outcome..
    """
    puf_generator = models.ForeignKey(PUFGenerator, on_delete=models.CASCADE)
    base_challenge = models.IntegerField(default=0, help_text="Enter the challenge as a decimal value and the system will truncate or add zeros to the most significant bit side (e.g., 12 will be converted to 1100 and then padded to 001100 if the PUF has 6 stages)")
    test_challenge = models.IntegerField(default=0, help_text="Enter the challenge as a decimal value and the system will truncate or add zeros to the most significant bit side (e.g., 12 will be converted to 1100 and then padded to 001100 if the PUF has 6 stages)")
    number_of_pufs = models.IntegerField(default=100)

    class Meta:
        verbose_name = 'Challenge Pair Analyzer'

    def __str__(self):
        return "ChallengePairAnalyzer[{0}, base_challenge={1}, test_challenge={2}, n_pufs={3}]".format(self.puf_generator, self.base_challenge, self.test_challenge, self.number_of_pufs)

    def run(self):
        """
        Build pufs, process them while updating progress, return data.
        """
        data = 0
        for i in range(self.number_of_pufs):
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
    Sample PUF `n` times and then find close neighbors to predict.
    """
    puf_generator = models.ForeignKey(PUFGenerator, on_delete=models.CASCADE)
    distance_choices = [
        ('gamma', 'gamma'),
        ('hamming', 'hamming'),
    ]
    k = models.IntegerField(default=1)
    distance = models.TextField(default='gamma', max_length=30, choices=distance_choices)
    known_set_limit = models.IntegerField(default=2, help_text="The predictor will iterate over `n` from `k` to `known_set_limit`, where `n` is the known set size that we use to predict the next challenge.")
    number_of_pufs = models.IntegerField(default=100)

    class Meta:
        verbose_name = 'Neighbor Predictor'

    def __str__(self):
        return "NeighborPredictor[{0}, k={1}, known_set_limit={2}, n_pufs={3}]".format(self.puf_generator, self.k, self.known_set_limit, self.number_of_pufs)

    def run(self):
        """
        Build pufs, process them while updating progress, return data.
        """
        data = [0 for x in range(self.known_set_limit+1)]
        for i in range(self.number_of_pufs):
            self.progress = int(i*100 / self.number_of_pufs)
            self.save()
            p = self.puf_generator.generate_puf()
            for j in range(self.k, self.known_set_limit+1):
                # randomly generate j crps
                crps = p.generate_random_crps(j)
                # randomly generate challenge
                ch = pl.generate_random_challenges(1, self.puf_generator.stages)[0]
                # find k closest crps and average them
                ordered = [] # tuples of (distance, c, r)
                for (c, r) in crps:
                    if self.distance == 'gamma':
                        ordered.append((pl.gamma(c, ch), c, r))
                    else:
                        ordered.append((pl.hamming(c, ch), c, r))
                ordered.sort(key=lambda tup: abs(tup[0]), reverse=True)
                match_total = 0
                match_sum = 0
                for n in range(self.k):
                    match_total += 1
                    bet = int(ordered[n][2])
                    if ordered[n][0] < 0:
                        bet = 0 if bet else 1
                    match_sum += bet
                # average them and round
                try:
                    prediction = match_sum / match_total
                    prediction = 1 if prediction >= 0.5 else 0
                except ZeroDivisionError:
                    prediction = np.random.choice([0, 1])
                # add to histogram if we successfully predicted the result
                true = int(p.run(ch))
                if prediction == true: data[j] += 1
        self.progress = 100
        self.data = data
        self.save()
        return data
