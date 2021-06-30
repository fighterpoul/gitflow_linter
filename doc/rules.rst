
.. GENERATED, DO NOT EDIT MANUALLY!!!

Rules
~~~~~

.. csv-table:: Available rules
    :header: "Rule", "Description"
    :widths: 15, 30

	"``single_master_and_develop``","gitflow strongly relies on the fact that there is only one branch for keeping the release history 
    and only one integration branch"
	"``no_old_development_branches``","having old feature or bugfix branches may create a mess in the repository
    
    use ``max_days_features`` option to configure what 'old' means for you"
	"``no_orphan_branches``","having branches that are out of configured folders (eg. created out of feature/, bugfix/) may be an 
    indicator that you do something wrong and create a mess in the repo"
	"``master_must_have_tags``","if your master branch contains commits that are not tagged, it probably means that you don't use 
    master as your releases history keeper"
	"``version_names_follow_convention``","checks if release branches and tags follow version naming convention
    
    the convention must be specified in ``version_regex`` argument as a regular expression string"
	"``no_dead_releases``","release branches that are not closed may create a mess in the repository and breaks the master/main 
    branch - releases must be closed as soon as they are deployed to production environment (or just before, 
    depending on your case)
    
    configure how long releases are supposed to be maintained by using ``deadline_to_close_release`` (number of days)"
	"``no_dependant_features``","creating feature/bugfix branches one from another or merging them together before merging to develop 
    may result in ugly issues during code review and merge mistakes 
    
    creating such a feature/merge is sometimes inevitable, you must configure the limit of such branches by using 
    ``max_dependant_branches`` option"
