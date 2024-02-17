# artefact_lister.py
from ara_tools.file_classifier import FileClassifier
from ara_tools.template_manager import DirectoryNavigator
import os

class ArtefactLister:
    def __init__(self, file_system=None):
        self.file_system = file_system or os

    def list_files(self, tags=None):
        # make sure this function is always called from the ara top level directory
        navigator = DirectoryNavigator()
        navigator.navigate_to_target()
        
        file_classifier = FileClassifier(self.file_system)
        classified_files = file_classifier.classify_files(tags=tags)
        file_classifier.print_classified_files(classified_files)
