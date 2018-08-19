from django.db import models
import numpy as np
import puflib as pl


class PDF(models.Model):
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
        return '{0}[{1}({2})]'.format(
            self.id,
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


class PUFGenerator(models.Model):
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

    def __str__(self):
        return "{0}[{1}, {2}, {3}]".format(self.architecture, self.stages, self.production_pdf, self.sample_pdf)

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


class BitflipAnalyzer(models.Model):
    """
    Build many PUFs and test challenges with bitflips to examine how often the
    response changes.
    """
    puf_generator = models.ForeignKey(PUFGenerator, on_delete=models.CASCADE)
    base_challenge = models.IntegerField(default=0, help_text="Enter the challenge as a decimal value and the system will truncate or add zeros to the most significant bit side (e.g., 12 will be converted to 1100 and then padded to 001100 if the PUF has 6 stages)")
    number_of_pufs = models.IntegerField(default=100)
    
    def __str__(self):
        return "{0}[{1}, {2}, {3}]".format(self.id, self.puf_generator, self.base_challenge, self.number_of_pufs)

    def run(self):
        """
        Build pufs, process them, return data.
        """
        data = [0 for x in range(self.puf_generator.stages)]
        for i in range(self.number_of_pufs):
            p = self.puf_generator.generate_puf()
            for j in range(len(p.stages)):
                c = p.get_bitstring(self.base_challenge)
                # flip j'th bit
                c_prime = c[:len(c)-j-1] + ('0' if c[len(c)-j-1] == '1' else '1') + c[len(c)-j:]
                t1 = p.run(c)
                t2 = p.run(c_prime)
                if t1 != t2: data[j] += 1
        return data
