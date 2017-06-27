from datetime import datetime
from django.conf import settings
from django.db import models
from xml.etree import ElementTree

from lib.cloudshell.api.cloudshell_api import CloudShellAPISession


class Family(models.Model):
    description = models.TextField(null=False)
    name = models.CharField(max_length=100, blank=False, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Model(models.Model):
    description = models.TextField(null=False)
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name='models')
    name = models.CharField(max_length=100, blank=False, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class RefreshFamiliesAndModels:
    def __init__(self):
        update_start_time = datetime.now()

        self.cs_session = CloudShellAPISession(host=settings.CLOUDSHELL['SERVER'],
                                               username=settings.CLOUDSHELL['USERNAME'],
                                               password=settings.CLOUDSHELL['PASSWORD'],
                                               domain=settings.CLOUDSHELL['DOMAIN'])

        raw_xml = self.cs_session.export_families_and_models().Configuration
        root = ElementTree.fromstring(raw_xml.strip())

        family_dict = {}
        resource_families = root.find('{http://schemas.qualisystems.com/ResourceManagement/ExportImportConfigurationSchema.xsd}ResourceFamilies')

        for family in list(resource_families):
            if 'ResourceType' in family.attrib and family.attrib['ResourceType'] == 'Resource':
                family_dict[family.attrib['Name']] = []
                print(family.attrib['Name'])

                resource_family, family_created = Family.objects.get_or_create(name=family.attrib['Name'])
                resource_family.description = family.get('Description', '')
                resource_family.save()

                resource_models = family.find('{http://schemas.qualisystems.com/ResourceManagement/ExportImportConfigurationSchema.xsd}Models')
                for model in list(resource_models):
                    family_dict[family.attrib['Name']].append(model.attrib['Name'])
                    print("\t", model.attrib['Name'])

                    resource_model, model_created = Model.objects.get_or_create(name=model.attrib['Name'],
                                                                                family=resource_family)
                    resource_model.description = model.get('Description', '')
                    resource_model.save()

        return
