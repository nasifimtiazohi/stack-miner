import re

import pandas as pd
import sys
import datetime
import time
import os

import requests
import xmltodict as xd
import logging

import gbls
import utils
class NvdCve(object):
    """Input, parse, persist NIST CVE vulnerability data.
    The NIST National Vulnerability Database ("NVD") is:
        "the U.S. government repository of standards based vulnerability
        management data."
    From https://nvd.nist.gov/download.cfm:
        XML Vulnerability Feeds - security related software flaws contained
        within XML documents. Each vulnerability in the file includes a
        description and associated reference links from the CVE dictionary
        feed, as well as a CVSS base score, vulnerable product configuration,
        and weakness categorization.
    "CVE" == "Common Vulnerabilities and Exposures". Each CVE entry describes
    "a known vulnerability. Included in the CVE entry are the CVSS scores.
    "CVSS" == "Common Vulnerability Scoring System". This is a set of metrics
    "to assess the severity / impact of a security vulnerability.
    Following is a typical NVD CVE entry from the XML flat file:
    ::
        <entry id="CVE-2015-1683">
            <vuln:vulnerable-configuration id="http://www.nist.gov/">
                <cpe-lang:logical-test operator="OR" negate="false">
                  <cpe-lang:fact-ref name="cpe:/a:microsoft:office:2007:sp3"/>
                </cpe-lang:logical-test>
            </vuln:vulnerable-configuration>
            <vuln:vulnerable-software-list>
                <vuln:product>
                    cpe:/a:microsoft:office:2007:sp3
                </vuln:product>
            </vuln:vulnerable-software-list>
            <vuln:cve-id>CVE-2015-1683</vuln:cve-id>
            <vuln:published-datetime>
                2015-05-13T06:59:14.880-04:00
            </vuln:published-datetime>
            <vuln:last-modified-datetime>
                2015-05-13T11:57:28.013-04:00
            </vuln:last-modified-datetime>
            <vuln:cvss>
              <cvss:base_metrics>
                <cvss:score>9.3</cvss:score>
                <cvss:access-vector>NETWORK</cvss:access-vector>
                <cvss:access-complexity>MEDIUM</cvss:access-complexity>
                <cvss:authentication>NONE</cvss:authentication>
                <cvss:confidentiality-impact>
                    COMPLETE
                </cvss:confidentiality-impact>
                <cvss:integrity-impact>COMPLETE</cvss:integrity-impact>
                <cvss:availability-impact>COMPLETE</cvss:availability-impact>
                <cvss:source>http://nvd.nist.gov</cvss:source>
                <cvss:generated-on-datetime>
                    2015-05-13T11:55:11.580-04:00
                </cvss:generated-on-datetime>
              </cvss:base_metrics>
            </vuln:cvss>
            <vuln:cwe id="CWE-119"/>
            <vuln:references xml:lang="en" reference_type="VENDOR_ADVISORY">
              <vuln:source>MS</vuln:source>
              <vuln:reference
                href="http://technet.microsoft.com/security/bulletin/MS15-046"
                xml:lang="en">
                MS15-046
              </vuln:reference>
            </vuln:references>
            <vuln:summary>
              Microsoft Office 2007 SP3 allows remote attackers to
              execute arbitrary code via a crafted document, aka "Microsoft
              Office Memory Corruption Vulnerability."
            </vuln:summary>
        </entry>
    **TL;DR: The NIST NVD is an standards-based repository of vulnerabilities.
    The vendor and software names can be found in the NIST CPE dictionary.**
    The I/P XML data is parsed, relevant data is extracted and then placed in
    a pandas dataframe.
    Methods
    -------
    __init__    Class constructor to configure logging, initialize empty data
                frame
    download_cve    Download NVD CVE XML feed data from the NIST website
    read        Input the NVD CVE data from the raw XML file. Clean data and
                remove columns. Extract the nested XML data to form a
                simple pandas dataframe.
    load        Load CVE dataframe from the serialized pickled file.
    save        Save the CVE dataframe to the corresponding pickled file.
    get         Return a *copy* of the CVE dataframe.
    """

    def __init__(self, mylogger=None):
        """Initialize class by configuring logging,  initializing dataframe.
        This is the class constructor. It initializes logging and allocates
        an empty dataframe to contain sccm hosts data.
        I/P Parameters
        --------------
        mylogger    logging object. If None, then a new object is initialzed.
        """
        # Configure logging

        if mylogger is None:
            self.logger = logging.getLogger(__name__)
            self.logger.setLevel(gbls.loglvl)
        else:
            self.logger = mylogger

        self.logger.info('Initializing NvdCve class')

        self.df_cve = pd.DataFrame({
            #   Fields in NVD software record
            'vuln:cve-id': [],
            'vuln:product': [],
            'cvss:access-complexity': [],
            'cvss:access-vector': [],
            'cvss:authentication': [],
            'cvss:availability-impact': [],
            'cvss:confidentiality-impact': [],
            'cvss:integrity-impact': [],
            'cvss:score': [],
            # 170118 Bug fix - Key error, sometimes not present
            #            'vuln:security-protection': [],
            'cvss:source': []

            #   Fields added during processing
            })

    def download_cve(self):
        """Download NIST CVE XML feed data and store in local directory.
        The NVD CVE ("Common Vulnerabilities and Exposures") XML flat files
        are downloaded. These files list known vulnerabilities.
        The data is supplied as a series of files - one file for each
        year. As vulnerability information is updated, files from previous
        years can be updated depending on when the vulnerability was
        discovered.
        For each year, there is also a small file with "meta" data
        describing the main XML file: Time of last update, file size, hash
        of file contents. NIST's intention is apparently twofold: a) limit
        B/W requirements by avoiding downloads of files that have not
        changed, b) protect integrity of downloaded data.
        Actions
        -------
            Determine current year. Allocate download directory if it does not
            exist.
            For each year to be processed:
                Download that year's meta file.
                Compare meta file contents with previous meta file (if it
                exists)
                If meta file contents have changed, then download the updated
                XML Feed file.
                The XML file is unzipped and stored in the download directory.
        Exceptions
        ----------
        RequestException:   The requests module, used for https access, has
                            several exception conditions.
        Returns
        -------
        None
        """

        # Determine current year
        now = datetime.datetime.now()
        my_yr = now.year

        # Process cve files for last "n" years

        for index in range(gbls.num_nvd_files):
            yr_processed = my_yr - index
            self.logger.info(
                '\n\nProcessing NVD files for {0}\n'.format(yr_processed)
                )

            # get the meta file for the year being processed
            url_meta = (
                        gbls.url_meta_base
                        + str(yr_processed)
                        + gbls.url_meta_end
                        )
            self.logger.info(
                '\nReading meta file: \n{0}\n\n'.format(
                                url_meta
                                )
                )
            try:
                resp = requests.get(url_meta)

            except requests.exceptions.RequestException as e:
                    self.logger.critical(
                        '\n\n***NVD XML feeds - Error: '
                        '\n{0}\n{0}\n\n'.format(
                            url_meta,
                            e
                            )
                        )
                    continue

            meta_filename = (
                            gbls.nvddir
                            + gbls.nvd_meta_filename
                            + str(yr_processed)
                            )

            # if file already exists then read the contents
            if os.path.isfile(meta_filename):
                meta_filecontents = open(meta_filename, 'r').read()

                # read updated xml feed file since corresponding meta file
                # contents have changed.

                if meta_filecontents == resp.text:

                    self.logger.info(
                        '\nMeta file unchanged, continuing.\n{0}\n\n'.format(
                                                    meta_filename
                                                    )
                        )
                    continue
                else:
                    self.logger.debug(
                        '\nMeta files differ:\n'
                        '   Current file: {0}\n'
                        '   File read from NVD: {1}\n\n'.format(
                                                    meta_filecontents,
                                                    resp.text
                                                    )
                        )
            else:
                self.logger.debug('\nMeta file does not exist:{0}'.format(
                                                    meta_filename
                                                    )
                                )

            # save new / updated meta file to disk

            output_meta = open(meta_filename, 'w')
            output_meta.write(resp.text)
            output_meta.close()

            # Read the new XML feed file

            url_xml = (
                        gbls.url_xml_base
                        + str(yr_processed)
                        + gbls.url_xml_end
                        )

            (xml_filename, xml_filecontents) = utils.get_zip(url_xml)

            # write this new / updated xml feed file to disk as well

            if xml_filename:

                # hardcode the filenames to avoid problems if NIST changes
                # names

                my_cve_filename = (
                            gbls.nvdcve
                            + str(yr_processed)
                            + '.xml'
                            )

                self.logger.info(
                    '\nSaving XML file I/P {0} as {1}\n\n'.format(
                                                xml_filename,
                                                my_cve_filename
                                                )
                    )

                output_xml = open(my_cve_filename, 'wb')
                output_xml.write(xml_filecontents)
                output_xml.close()

        return None

    def read(self, my_dir=None):
        """Read the CVE XML file, parse, and store in pandas dataframe.
        Actions
        -------
        The NVD CVE ("Common Vulnerabilities and Exposures") XML flat file is
        read. This file contains a list of known vulnerabilities. The venodor
        and software names can be found in the NIST CPE dictionary.
        * The data is supplied in a series of files. There is one file for
          each year. As vulnerability information is updated, files from
          previous years can be updated depending on when the vulnerability
          was discovered.
          Each files is read, parsed into a python dictionary, then converted
          to a pandas dataframe.
          All of these individual data frames are appended to form one
          dataframe.
        * The data is cleaned by eliminating null entries.
        * The nested XML data is painstakingly extracted. The data from the
          corresponding python dictionaries and lists is used to populate new
          columns in the main pandas dataframe.   loaded into a pandas
          dataframe.
        *  The data is cleaned further by removing "OS" and "Hardware"
           entries. Extraneous columns are also dropped.
        *  The CVSS ("Common Vulnerability Scoring System" data in the CVE
           entry is extracted and used to populate additional columns in the
           dataframe.
        Exceptions
        ----------
        IOError:    Log an error message and ignore
        Returns
        -------
        None
        """
        self.logger.info('\n\nEntering NvdCve.read\n\n')

        # Read in the uncompressed NVD XML data
        try:
            fst_time = True

            if my_dir is None:
                my_dir = gbls.nvddir

            # List directory contents

            f = []

            for (dirpath, dirnames, filenames) in os.walk(my_dir):
                f.extend(filenames)
                break

            # Iterate through the cve files

            for my_file in filenames:

                # skip the cpe dictionary if it is there

                if not my_file.startswith(gbls.cve_filename):
                    continue

                my_file1 = my_dir + my_file

                self.logger.info(
                        '\nReading {0}\n\n'.format(
                            my_file1
                            )
                        )

                with open(my_file1) as fd:
                    my_dict = xd.parse(fd.read())

                df_tmp = pd.DataFrame.from_dict(
                            my_dict['nvd']['entry']
                            )
                if fst_time:
                    df_nvd = df_tmp
                    fst_time = False
                else:
                    df_nvd = df_nvd.append(df_tmp)

        except IOError as e:
            self.logger.critical('\n\n***I/O error({0}): {1}\n\n'.format(
                        e.errno, e.strerror))
        except:
            self.logger.critical(
                '\n\n***Unexpected error: {0}\n\n'.format(
                    sys.exc_info()[0]))
            raise

        self.logger.info(
            '\n\nNVD CVE raw data input counts: \n{0}\n{1}\n\n'.format(
                    df_nvd.shape,
                    df_nvd.columns
                    )
            )

        # eliminate null entries. Then reset index to sequential #'s
        df_nvd1 = df_nvd[
                df_nvd['vuln:cvss'].notnull()
                ].reset_index(drop=True)

        self.logger.debug(
            '\n\nNVD CVE data after eliminating '
            'null entries: \n{0}\n\n'.format(
                    df_nvd1.shape
                    )
            )

        # pull out cvss_dict hierarchical entry in each row
        s_cvss_dict = df_nvd1['vuln:cvss'].apply(
                        lambda mydict: mydict['cvss:base_metrics']
                        )

        # convert this series to a dataframe
        df_cvss = pd.DataFrame(s_cvss_dict.tolist())

        # Finally, concatenate the two dataframes into one (by columns)
        df_nvd2 = pd.concat([df_nvd1, df_cvss], axis=1, join='outer')

        self.logger.debug(
            '\n\nNVD CVE counts, columns after '
            'pulling out embedded CVSS data: \n{0}\n{1}\n\n'.format(
                        df_nvd2.shape,
                        df_nvd2.columns
                        )
            )

        # drop unneeded columns
        df_nvd2.drop(
                ['@id', 'vuln:cwe'],
                axis=1,
                inplace=True
                )

        # Build a table of vulns vs software

        # extract list of impacted software for each vulnerability
        # build a new dataframe with the vuln's cve-id
        df_sft = df_nvd2[['vuln:cve-id']]

        # then pull out the embedded list of vulnerable software
        # and if the software list is empty, then handle this gracefully
        df_sft['sftlist'] = df_nvd2[
            'vuln:vulnerable-software-list'].fillna(value='xx').apply(
                lambda mydict: [] if mydict == 'xx' else mydict[
                                                            'vuln:product'
                                                            ]
                )

        self.logger.info(
                '\n\n embedded software counts: \n{0}'.format(
                                df_sft.shape
                                )
                )

        # expand each embedded software list into a list containing tuples of
        # the form ['cve_id', 'software_id']

        # initialize an empty list
        lst_sft = []

        # This fn pulls out the embedded list and builds the tuples
        def myfn3(row):
            mylist = row['sftlist']

            # handle case where there is only 1 vuln software in the list
            if not(isinstance(mylist, list)):
                    mylist = [mylist]

            # append each new tuple onto the end of the existing list
            for sft in mylist:
                lst_sft.append([row['vuln:cve-id'], sft])

            # return some value to keep pandas happy
            return 1

        # Run through the dataframe and apply the fn to each row in turn
        df_sft.apply(myfn3, axis=1)

        # Now convert the list of tuples to a dataframe
        df_sft1 = pd.DataFrame(
                lst_sft,
                columns=['vuln:cve-id', 'vuln:product']
                )

        # remove os/hdware entries. Best to analyze MS OS vulns by using MS'
        # patch csv file

        pattern = re.compile(
                        'cpe:'
                        '/[oh]:',
                        re.IGNORECASE | re.UNICODE
                        )

        df_sft2 = df_sft1[
                        ~df_sft1['vuln:product'].str.contains(pattern)
                        ]

        # Finally add information describing the vulnerability add in cvss
        # information concerning the vuln characteristics and severity

        # pull out the cvss information for each vulnerability
        df_cvss = df_nvd2[[
                'vuln:cve-id',
                u'cvss:access-complexity',
                u'cvss:access-vector',
                u'cvss:authentication',
                u'cvss:availability-impact',
                u'cvss:confidentiality-impact',
                u'cvss:integrity-impact',
                u'cvss:score',
                # 170118 Bug fix: Sometimes not present
                #                u'vuln:security-protection',
                u'cvss:source'
                ]]

        # Now merge it into the new dataframe mapping software to vulns
        self.df_cve = pd.merge(
                        df_sft2,
                        df_cvss,
                        how='inner',
                        on='vuln:cve-id'
                        )

        self.logger.info(
                        '\n\nUpdated software dataframe '
                        'which maps software to vulns: \n{0}\n{1}\n\n'.format(
                                self.df_cve.shape,
                                self.df_cve.columns
                                )
                        )

        return None

    def load(self, mypck=None):
        """Load NvdCve vulnerability dataframe that was previously saved."""
        self.logger.info(
                '\n\nLoading saved CVE data into '
                'NvdCve.df_cve dataframe\n\n'
                )
        if mypck is None:
            mypck = gbls.df_cve_pck

        self.df_cve = pd.read_pickle(mypck)
        return None

    def save(self):
        """Save NvdCpe vuln dataframe in serialized pickle format."""
        self.logger.info('\n\nSaving NvdCve.df_cve dataframe\n\n')
        self.df_cve.to_pickle(gbls.df_cve_pck)
        return None

    def get(self):
        """Return a *copy* of the data."""
        df_tmp = self.df_cve.copy()
        self.logger.info(
                '\n\nGet NvdCve.df_cve: \n{0}\n{1}\n\n'.format(
                                df_tmp.shape,
                                df_tmp.columns
                                )
                )
        return df_tmp