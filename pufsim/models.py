from django.db import models
import numpy as np
import puflib as pl


class PDF(models.Model):
    """
    Represents a probability distribution function
    """
    name = models.CharField(max_length=255)
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

    model_order = 1

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
        return self.name

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
    Model for building delay-based PUFs
    """
    name = models.CharField(max_length=255)
    archs = [
        ('loop', 'loop'),
        ('arbiter', 'arbiter'),
    ]
    architecture = models.CharField(max_length=30, choices=archs)
    stages = models.IntegerField(default=10)
    production_pdf = models.ForeignKey(PDF, verbose_name='Production PDF', on_delete=models.CASCADE, help_text='Variance during initial production of the PUF.')
    sample_pdf = models.ForeignKey(PDF, verbose_name='Sample PDF', on_delete=models.CASCADE, related_name='sample_pdf_revacc', help_text='Variance each time the produced PUF is sampled.')
    sensitivity = models.FloatField(default=0.0, help_text='If the difference in delay of the two signal paths in the PUF is less than this value, then the result will be random. Otherwise, the result is deterministic.')

    model_order = 2

    class Meta:
        verbose_name = 'PUF Generator'

    def __str__(self):
        return self.name

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


class CompositePUFGenerator(models.Model):
    """
    Model for building delay-based composite PUFs
    """
    name = models.CharField(max_length=255)
    archs = [
        ('xor', 'xor'),
    ]
    architecture = models.CharField(max_length=30, choices=archs)
    child_architecture = models.ForeignKey(PUFGenerator, on_delete=models.PROTECT)
    levels = models.IntegerField(default=10)

    model_order = 3

    @property
    def stages(self):
        return self.child_architecture.stages

    class Meta:
        verbose_name = 'Composite PUF Generator'

    def __str__(self):
        return self.name

    def generate_puf(self):
        """
        Generate a Composite PUF based on the specifications.
        """
        if self.architecture == 'xor':
            return pl.Xor(pufs=[self.child_architecture.generate_puf() for x in range(self.levels)])
        return None
