# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['majormode',
 'majormode.xebus',
 'majormode.xebus.sis',
 'majormode.xebus.sis.connector',
 'majormode.xebus.sis.connector.sis']

package_data = \
{'': ['*']}

install_requires = \
['perseus-core-library>=1.19,<2.0',
 'perseus-getenv-library>=1.0,<2.0',
 'requests>=2.31,<3.0',
 'xebus-core-library>=1.4,<2.0',
 'xebus-sis-connector-core-library>=0.0,<0.1']

setup_kwargs = {
    'name': 'xebus-sis-connector-eduka',
    'version': '1.0.0',
    'description': "Connector to fetch data from a school's Eduka information system",
    'long_description': '# Xebus Eduka SIS Connector\nConnector to fetch data from a school\'s Eduka information system.\n\n```csv\n"Code identifiant";"Nom";"Prénom";"Nom complet";"Nationalité 1";"Langue maternelle";"Date de naissance";"Age";"Branche scolaire";"Classe";"Code identifiant R1";"Code identifiant R2";"Prénom R1";"Prénom R2";"Nom R1";"Nom R2";"Nom complet R1";"Nom complet R2";"Langue(s) parlée(s) R1";"Langue(s) parlée(s) R2";"Nationalité(s) R1";"Nationalité(s) R2";"Adresse e-mail R1";"Adresse e-mail R2";"Téléphone mobile R1";"Téléphone mobile R2";"Street R1";"Street R2"\n"12046S3485";"CAUNE NGUYEN";"Éline Xuân Anh Aurora";"CAUNE NGUYEN Éline Xuân Anh Aurora";"French";"Vietnamese";"23/12/2016";"7";"Elementaire » Cours élémentaire 1 (Ce1)";"CE1 B";"12046G3483";"12046G3482";"Thi Thanh Truc";"Daniel";"NGUYEN";"CAUNE";"NGUYEN Thi Thanh Truc";"CAUNE Daniel";"French, English, Vietnamese";"French, English, Vietnamese";"Vietnamese";"French";"thithanhtruc.nguyen@gmail.com";"daniel.caune@gmail.com";"+84 822 170 781";"+84 812 170 781";"18A Võ Trường Toản, P. An Phú, Quận 2, TP.HCM";"18A Võ Trường Toản, P. An Phú, Quận 2, TP.HCM"\n```\n\nList of the CSV fields:\n\nSection **Child**\n\n| Eduka Field Name  | Description                                                                                           | Xebus Field Name |\n|-------------------|-------------------------------------------------------------------------------------------------------|------------------|\n| Code identifiant  | The child’s unique identifier as referenced in the school organization’s information system (SIS).    | SIS ID           |\n| Prénom            | The given name of the child.                                                                          | First Name       |\n| Nom               | The surname of the child.                                                                             | Last Name        |\n| Nom complet       | The complete personal name of the child, including their last name, first name and middle name(s).    | Full Name        |\n| Langue maternelle | The spoken language of the child.                                                                     | Language         |\n| Nationalité 1     | The primary nationality of the child.                                                                 | Nationality      |\n| Date de naissance | The date of birth of the child, in the format `DD/MM/YYYY`.                                           |                  | Date of Birth    |\n| Branche scolaire  | The name of the education grade that the child has reached for the current or the coming school year. | Grade Name       |\n| Classe            | The name of the class that the child has enrolled for the current or the coming school year.          | Class Name       |\n\nSection **Primary Parent**\n\n| Eduka Field Name       | Description                                                                                                 | Xebus Field Name |\n|------------------------|-------------------------------------------------------------------------------------------------------------|------------------|\n| Code identifiant R1    | The primary parent’s unique identifier as referenced in the school organization’s information system (SIS). | SIS ID           |\n| Prénom R1              | The first name (also known as the given name) of the primary parent.                                        | First Name       |\n| Nom R1                 | The surname of the primary parent.                                                                          | Last Name        |\n| Nom complet R1         | The complete personal name of the primary parent, including their surname, first name and middle name(s).   | Full Name        |\n| Langue(s) parlée(s) R1 | The preferred language of the primary parent.                                                               | Language         |\n| Nationalité(s) R1      | The primary nationality of the primary parent.                                                              | Nationality      |\n| Adresse e-mail R1      | The email address of the primary parent.                                                                    | Email Address    |\n| Téléphone mobile R1    | The international mobile phone number of the primary parent.                                                | Phone Number     |\n| Street R1              | The address of the home where the primary parent accommodates their child.                                  | Home Address     |\n\nSection **Secondary Parent**\n\n| Eduka Field Name       | Description                                                                                                   | Xebus Field Name |\n|------------------------|---------------------------------------------------------------------------------------------------------------|------------------|\n| Code identifiant R2    | The secondary parent’s unique identifier as referenced in the school organization’s information system (SIS). | SIS ID           |\n| Prénom R2              | The first name (also known as the given name) of the secondary parent.                                        | First Name       |\n| Nom R2                 | The surname of the secondary parent.                                                                          | Last Name        |\n| Nom complet R2         | The complete personal name of the secondary parent, including their surname, first name and middle name(s).   | Full Name        |\n| Langue(s) parlée(s) R2 | The preferred language of the secondary parent.                                                               | Language         |\n| Nationalité(s) R2      | The primary nationality of the secondary parent.                                                              | Nationality      |\n| Adresse e-mail R2      | The email address of the secondary parent.                                                                    | Email Address    |\n| Téléphone mobile R2    | The international mobile phone number of the secondary parent.                                                | Phone Number     |\n| Street R2              | The address of the home where the secondary parent accommodates their child.                                  | Home Address     |\n\n\n## Languages & Nationalities\n\n| Name             |\n|------------------|\n| Dutch            |\n| English          |\n| French           | \n| German           |\n| Italian          |\n| Japanese         |\n| Mandarin Chinese |\n| Polish           |\n| Portuguese       |\n| Russian          |\n| Spanish          |',
    'author': 'Daniel CAUNE',
    'author_email': 'daniel.caune@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/xebus/xebus-sis-connector-eduka',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
