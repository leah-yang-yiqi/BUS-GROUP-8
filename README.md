### Brief description of the system and its purpose

The **original purpose of building this code project** was to complete Assignment-Part 2 of the University of Birmingham's Building Usable Software course. During the development process, we built upon the project documentation from Assignment-Part 1 to design and implement three core modules: 

* **AI Dialogue **
* **Accessibility Support**
* **Cost of Living Support**

Detailed functionalities and implementation specifics of each module will be introduced in subsequent sections of the project's README.md file.

Throughout the development of this code prototype, we adhered to sound software design principles and architectural patterns. 

Regarding design principles, we **primarily implemented the Interface Segregation Principle and Open-Closed Principle.**

*  The Interface Segregation Principle ensured low coupling between modules, where each module only depends on minimal required interfaces, enhancing code maintainability and extensibility. 
* The Open-Closed Principle guarantees that the code can be conveniently extended and upgraded without modifying existing implementations.

In terms of architectural design, we **adopted the classic MVC (Model-View-Controller) architecture**. This pattern separates application logic, user interface, and data storage, resulting in clearer code structure and easier development/maintenance.

Additionally, the **Decorator Pattern** was strictly followed throughout the project's development process.



### **How to Run This Project**

First, you need to download this repository:

```
git https://github.com/JiaxinHou-123/BUS-GROUP-8.git
```

Then install the dependencies using pip:

```
pip install -r requirements.txt
```

To ensure the correct version of torch, please install it strictly in accordance with the instructions in the  [official documentation](https://pytorch.org/get-started/locally/) .

Enter the following instructions in the terminal to run:

```
python app.py
```

Due to considerations of computational resources, we built the project to run on a cloud server. To enable local computer access, we configured port forwarding. During actual runtime, you can use the following commands to retrieve the host and port information:

```
python app.py --host 0.0.0.0 --port 8080
```



### Environmental configuration

This project is developed **using Python, with the Flask framework constructing the backend architecture, and integrates PyTorch and ModelScope libraries to build core components of the AI dialogue system**. At the model level, we adopted the open-source [ChatGLM3-6b](https://github.com/THUDM/ChatGLM3) large language model (6-billion-parameter scale) from ZhipuAI as the foundational architecture. While model fine-tuning was omitted due to computational resource constraints and insufficient training data, the system maintains basic conversational functionality for standard interaction use cases.

For specific configuration requirements, please refer to the requirements.txt file



### A summary of implemented functionalities

###### AI Dialogue

For the AI Dialogue module, we have implemented conversational query and chat functionalities. Students can submit feedback through this interface, which is then stored in the backend's "datas/feedback.txt" file for subsequent analysis and processing.

###### Accessibility Support

The Accessibility Support Module implements the following functionalities: 

* Accessibility-related information (videos, photos, and text) is made available for user browsing and search operations; 
* An administrative interface enables authorized university staff to upload multimedia content (videos, images, and textual descriptions) documenting campus accessibility resources;
* Integrated search capabilities allow users to query up-to-date government allowances and grants, with automatic redirection functionality to relevant sections of the GOV.UK portal for official information access.
* Realize the feedback function

###### Cost of Living Support

The Cost of Living Support Module delivers the following key features: 

*  A budgeting utility provisioned by system administrators enables students to generate personalized living expense projections with tailored budgeting recommendations; 
  * Calculate the monthly/weekly/annual living expense budget based on students' quality of life needs. Students can switch the time units by themselves.
  * Realize the provision of allocation suggestions based on the current budget of students (retaining the calculator function), including referring to the weight of students' consumption preferences. If the predicted value exceeds the current budget, a reminder will be given
* Students can download selected multimedia content (instructional videos, infographics, and documents) uploaded by administrators that provide information on cost of living management strategies;
* An integrated portal provides access to auxiliary financial aid policies and campus employment resources, featuring a centralized repository for part-time job listings accompanied by CV optimization guidelines and automated application workflows via API integrations with university HR systems.
* The uploaded files can be read and deleted


###### Other

* The question-and-answer function of Accommodation has been implemented
* When a blank form is submitted, the indicated words will appear
* Import the database, log in and out, and register
* Realize user division, and different users see different interfaces



### contribution 
| Student Name &ID   | Contribution(%) | Key Contributions/Tasks Completed                            | Comments (if any)                                    | Signature  |
| ------------------ | --------------- | ------------------------------------------------------------ | ---------------------------------------------------- | ---------- |
| Jiaxin Hou-2746978 | 21%             | ① In the backend app.py file, the following functionalities were implemented:**AI Dialogue**: Chat interaction and feedback mechanism (with feedback stored in dedicated `/datas` directory);**Accessibility Support**: Resource search functionality (including downloadable resources via dedicated button);**Admin Controls**: Resource file upload with file type validation, integrated GOV.UK search redirection;**Cost of Living Support**: Multi-resource search system and dynamic cost-of-living budgeting tools<br/>②The overall writing of Readme and requirements.txt<br/>③Successfully migrated open-source LLM infrastructure and engineered the chat interface frontend. | Complete the initial code integration and git upload | Jiaxin Hou |
| Xi Feng- 2794920   | 21%             | ① Assisted in the development of app.py, including data querying, comment annotation, and code review.<br/>② Completed the development of the Accessibility Support frontend interface.<br/>③ Assisted with project integration.<br/>④ Assisted in the documentation of the Readme. | The writing of index.html                            | Xi Feng    |
| Zijun He- 2749467  | 21%             | ① Assisted in the development of app.py, including runtime checks and style consistency verification.<br/>② Completed the development of the Cost of Living Support frontend interface.<br/>③ Assisted with project integration.<br/>④ Contributed to the documentation of the Readme. | The writing of base.html                             | Zijun He   |
| Xiaoya Dou-2853070 | 18.5%           | ① Optimized the budgeting functionality for Cost of Living Support.<br/>② Implemented a recommendation feature for budget allocation based on students" current budgets (while retaining the calculator functionality).<br/>③ Enhanced handling of blank form submissions by displaying prompt messages.<br/>④ Added upload capability for image, text, and video resources. | The writing of "test"                                | Xiaoya Dou |
| Yiqi Yang- 2869896 | 18.5%           | ① Integrated database implementation and developed user login/logout, and registration functionalities.<br/>② Established role-based partitioning to enable differentiated interface views for distinct user roles.<br/>③ Enhanced the Accessibility Support module by implementing a feedback mechanism and integrating search box with resource display.<br/>④ Enhanced file management capabilities with viewing and deletion options for uploaded documents.<br/>⑤ Implemented an accommodation-focused Q&A feature within Accessibility Support. | The writing of "test"                                | Yiqi Yang  |

