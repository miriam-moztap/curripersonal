from django.db import models


class Module(models.Model):

    name = models.CharField(max_length=100, null=False, verbose_name='Name')
    description = models.CharField(
        max_length=100, null=False, verbose_name='Description')
    status_delete = models.BooleanField(
        default=False, verbose_name='Status Delete')

    class Meta:
        verbose_name = 'Module'
        verbose_name_plural = 'Modules'
        db_table = 'module'
        ordering = ('id', )


class Role(models.Model):

    name = models.CharField(max_length=100, null=False, verbose_name='Name')
    description = models.CharField(
        max_length=100, null=False, verbose_name='Description')
    isSuperAdmin = models.BooleanField(
        default=False, verbose_name='Super admin')
    status_delete = models.BooleanField(
        default=False, verbose_name='Status Delete')
    module = models.ManyToManyField(Module, through='RoleModule')
    host = models.CharField(max_length=100, null=False,
                            verbose_name='Host access')

    class Meta:
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'
        db_table = 'role'
        ordering = ('id', )


class RoleModule(models.Model):

    role = models.ForeignKey(
        Role, on_delete=models.CASCADE, verbose_name='Role_id')
    module = models.ForeignKey(
        Module, on_delete=models.CASCADE, verbose_name='Module_id')
    status = models.BooleanField(default=True, verbose_name='Status')
    status_delete = models.BooleanField(
        default=False, verbose_name='Status Delete')

    class Meta:
        verbose_name = 'Role_Module'
        verbose_name_plural = 'Role_Modules'
        db_table = 'role_module'
        ordering = ('id', )


class CVLanguage(models.Model):
    """Model for written CV Language."""

    language = models.CharField(
        max_length=100, null=False, blank=False, unique=True, verbose_name='CV Language'
    )
    status_delete = models.BooleanField(
        default=False, verbose_name='Status deletion'
    )
    created_date = models.DateField(
        auto_now_add=True, verbose_name='Created date'
    )
    modified_date = models.DateField(
        auto_now=True, verbose_name='Modified date'
    )

    class Meta:
        verbose_name = 'CV Language'
        verbose_name_plural = 'CV Languages'
        ordering = ('id',)
        db_table = 'cv_languages'

    def __str__(self):
        return str(self.language)

    def save(self, *args, **kwargs):
        self.language = self.language.lower()
        return super(CVLanguage, self).save(*args, **kwargs)

