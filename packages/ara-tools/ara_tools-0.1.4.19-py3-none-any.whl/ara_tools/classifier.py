class Classifier:

    valid_classifiers = {
        "vision": "vision",
        "businessgoal": "businessgoals",
        "capability": "capabilities",
        "keyfeature": "keyfeatures",
        "feature": "features",
        "epic": "epics",
        "userstory": "userstories",
        "task": "tasks",
        "tasklist": "tasks",
        "example": "examples",
    }
    
    classifier_order = [
        "vision",
        "businessgoal",
        "capability",
        "keyfeature",
        "epic",
        "userstory",
        "example",
        "feature",
        "task",
        "tasklist",
        "issue",
    ]

    artefact_title = {
        "vision": "Vision",
        "businessgoal": "Businessgoal",
        "capability": "Capability",
        "keyfeature": "Keyfeature",
        "epic": "Epic",
        "userstory": "Userstory",
        "example": "Example",
        "feature": "Feature",
        "task": "(?:Task list|Task)"
    }



    @staticmethod
    def get_sub_directory(classifier):
        return Classifier.valid_classifiers.get(classifier)

    @staticmethod
    def is_valid_classifier(classifier):
        return classifier in Classifier.valid_classifiers

    @staticmethod
    def ordered_classifiers():
        return Classifier.classifier_order

    @staticmethod
    def get_artefact_title(classifier):
        return Classifier.artefact_title.get(classifier)
