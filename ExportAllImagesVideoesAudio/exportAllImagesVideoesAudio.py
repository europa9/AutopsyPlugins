# File: exportAllImagesVideoesAudio.py
# Version 0.0.1
# Date 12:36 23.02.2020
# Copyright (c) 2020 S. A. Ditlefsen
# License: http://opensource.org/licenses/gpl-license.php GNU Public License
#

import jarray
import inspect
import os
from subprocess import Popen, PIPE
import json

from javax.swing import JCheckBox
from javax.swing import JButton
from javax.swing import ButtonGroup
from javax.swing import JTextField
from javax.swing import JLabel
from java.awt import GridLayout
from java.awt import GridBagLayout
from java.awt import GridBagConstraints
from javax.swing import JPanel
from javax.swing import JList
from javax.swing import JScrollPane
from javax.swing import JFileChooser
from javax.swing import JComboBox
from javax.swing import JPasswordField
from javax.swing.filechooser import FileNameExtensionFilter

from java.lang import Class
from java.lang import System
from java.sql  import DriverManager, SQLException
from java.util.logging import Level
from java.io import File
from org.sleuthkit.datamodel import SleuthkitCase
from org.sleuthkit.datamodel import AbstractFile
from org.sleuthkit.datamodel import ReadContentInputStream
from org.sleuthkit.datamodel import BlackboardArtifact
from org.sleuthkit.datamodel import BlackboardAttribute
from org.sleuthkit.datamodel import TskData
from org.sleuthkit.autopsy.ingest import IngestModule
from org.sleuthkit.autopsy.ingest.IngestModule import IngestModuleException
from org.sleuthkit.autopsy.ingest import DataSourceIngestModule
from org.sleuthkit.autopsy.ingest import IngestModuleFactoryAdapter
from org.sleuthkit.autopsy.ingest import GenericIngestModuleJobSettings
from org.sleuthkit.autopsy.ingest import IngestModuleIngestJobSettingsPanel
from org.sleuthkit.autopsy.ingest import IngestMessage
from org.sleuthkit.autopsy.ingest import IngestServices
from org.sleuthkit.autopsy.ingest import ModuleDataEvent
from org.sleuthkit.autopsy.coreutils import Logger
from org.sleuthkit.autopsy.coreutils import PlatformUtil
from org.sleuthkit.autopsy.casemodule import Case
from org.sleuthkit.autopsy.casemodule.services import Services
from org.sleuthkit.autopsy.casemodule.services import FileManager
from org.sleuthkit.autopsy.datamodel import ContentUtils


# Copy Multimedia Factory ---------------------------------------------------------------------------------------------------
class ExportAllImagesVideoesAudioFactory(IngestModuleFactoryAdapter):

    # TODO: give it a unique name.  Will be shown in module list, logs, etc.
    moduleName = "Export all images, videoes and audio ingest module"

    def getModuleDisplayName(self):
        return self.moduleName

    # TODO: Give it a description
    def getModuleDescription(self):
        return "Find all images, videoes and audio. It copies everything to a new folder. "

    def getModuleVersionNumber(self):
        return "1.0"

    # Return true if module wants to get called for each file
    def isFileIngestModuleFactory(self):
        return True

    # can return null if isFileIngestModuleFactory returns false
    def createFileIngestModule(self, ingestOptions):
        return ExportAllImagesVideoesAudio()

# Copy Multimedia ----------------------------------------------------------------------------------------------------------
class ExportAllImagesVideoesAudio(FileIngestModule):

    _logger = Logger.getLogger(ExportAllImagesVideoesAudioFactory.moduleName)

    def log(self, level, msg):
        self._logger.logp(level, self.__class__.__name__, inspect.stack()[1][3], msg)

    # Startup
    def startUp(self, context):
        self.filesFound = 0

        pass


    # Process
    def process(self, file):
        # Skip non-files
        if ((file.getType() == TskData.TSK_DB_FILES_TYPE_ENUM.UNALLOC_BLOCKS) or
            (file.getType() == TskData.TSK_DB_FILES_TYPE_ENUM.UNUSED_BLOCKS) or
            (file.isFile() == False)):
            return IngestModule.ProcessResult.OK

        # Blackboard
        blackboard = Case.getCurrentCase().getServices().getBlackboard()

        # List of images and videoes
        listOfMimeToCopy = ['image/bmp','image/gif', 'image/jpeg', 'image/png', 'image/tiff',
                                'image/vnd.adobe.photoshop', 'image/x-raw-nikon', 'image/x-ms-bmp', 'image/x-icon', 'image/webp',
                                'image/vnd.microsoft.icon', 'image/x-rgb', 'image/x-ms-bmp','image/x-xbitmap','image/x-portable-graymap',
                                'image/x-portable-bitmap', 
                                'video/webm', 'video/3gpp', 'video/3gpp2', 'video/ogg','video/mpeg', 
                                'video/mp4', 'video/quicktime', 'video/x-msvideo', 'video/x-flv', 'video/x-m4v', 
                                'video/x-ms-wmv', 
                                'audio/midi', 'audio/mpeg', 'audio/webm', 'audio/ogg', 'audio/wav', 
                                'audio/vnd.wave', 'audio/x-ms-wma']

        # Export directory (C:\Users\user\Documents\cases\1568795\Autopsy\1568795_2020_5060_90_1_sofias_pc\Export)
        exportDirectory = Case.getCurrentCase().getExportDirectory()
        caseName = Case.getCurrentCase().getName()
        number = Case.getCurrentCase().getNumber()
        exportDirectory = exportDirectory.replace("\\Autopsy", "");
        exportDirectory = exportDirectory.replace("\\" + str(number), "");
        exportDirectory = exportDirectory.replace("\\Export", "");
        ImgVideoAudioDirectory = os.path.join(exportDirectory, "Img_video_audio")
        self.log(Level.INFO, "==>exportDirectory=" + str(exportDirectory) + " number=" + str(number))
        try: 
                os.mkdir(ImgVideoAudioDirectory)
        except:
                self.log(Level.INFO, "")


        # For an example, we will flag files with .txt in the name and make a blackboard artifact.
        if(file.getMIMEType() in listOfMimeToCopy):

                # Recreate path
                uniquePathFullLinux = file.getUniquePath();
                
                # Recreate path Windows
                uniquePathFullWindows = uniquePathFullLinux.replace("/", "\\")
                uniquePathFullWindows = uniquePathFullWindows[1:]
                
                fileName = os.path.basename(uniquePathFullWindows)
                uniquePathWindows = uniquePathFullWindows.replace(fileName, "");
                
                # Create directory
                splitDir = uniquePathWindows.split("\\")
                pathToCreate = os.path.join(exportDirectory, "Img_video_audio")
                for directory in splitDir:
                        directory = directory.replace(":", "")
                        pathToCreate = os.path.join(pathToCreate, directory)
                        # self.log(Level.INFO, "==> directory=" + str(directory) + " pathToCreate=" + str(pathToCreate))

                        try: 
                                os.mkdir(pathToCreate)
                        except:
                                self.log(Level.INFO, "")

                # Write file
                try:
                        extractedFile = os.path.join(pathToCreate, file.getName())
                        ContentUtils.writeToFile(file, File(extractedFile))
                except:
                        self.log(Level.SEVERE, "Error writing File " + file.getName() + " to " + extractedFile)

                # Make artifact on blackboard
                art = file.newArtifact(BlackboardArtifact.ARTIFACT_TYPE.TSK_INTERESTING_FILE_HIT)
                att = BlackboardAttribute(BlackboardAttribute.ATTRIBUTE_TYPE.TSK_SET_NAME, ExportAllImagesVideoesAudioFactory.moduleName, "Images, videoes and audio")
                art.addAttribute(att)

                # Index artifact
                try:
                        # index the artifact for keyword search
                        blackboard.indexArtifact(art)
                except Blackboard.BlackboardException as e:
                        self.log(Level.SEVERE, "Error indexing artifact " + art.getDisplayName())

                # UI
                IngestServices.getInstance().fireModuleDataEvent(ModuleDataEvent(ExportAllImagesVideoesAudioFactory.moduleName, BlackboardArtifact.ARTIFACT_TYPE.TSK_INTERESTING_FILE_HIT, None))

        return IngestModule.ProcessResult.OK

    # Shutdown
    def shutDown(self):
        # As a final part of this example, we'll send a message to the ingest inbox with the number of files found (in this thread)
        message = IngestMessage.createMessage(
            IngestMessage.MessageType.DATA, ExportAllImagesVideoesAudioFactory.moduleName,
                str(self.filesFound) + " files found")
        ingestServices = IngestServices.getInstance().postMessage(message)
