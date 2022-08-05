from django.db import models

# Create your models here.

class Fab(models.TextChoices):
    T1 = 'T1', 'T1'
    T2 = 'T2', 'T2'

class Glass(models.TextChoices):
    EXG = 'EXG', 'EXG'

class PSModel(models.TextChoices):
    PS_214_R5 = '214-R5', '214-R5'
    PS_NN4104 = 'NN4104', 'NN4104'
    PS_700R_1 = '700R-1', '700R-1'
    PS_TG1553SA7 = 'TG1553SA7', 'TG1553SA7'
    
class MPSType(models.TextChoices):
    T = 'T type', 'T type'
    O = 'O type', 'O type'
    C = 'C type', 'C type'
    
class LCType(models.TextChoices):
    NLC = 'NLC', 'NLC'
    PLC = 'PLC', 'PLC'