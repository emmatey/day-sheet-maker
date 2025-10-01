<div style="text-align: center;">
![Document header.](https://raw.githubusercontent.com/emmatey/day-sheet-maker/refs/heads/react-ui/assets/readmeImages/documentHeader.png)
</div>

Daysheet maker is a bespoke utility for a specific workplace and task. Its primary, and only function is to convert Kronos schedules, automatically generated for retail managers at the relevant business, and transform them into “Daysheets”.

This tool is comprised of three sections, the ‘backend’ processing logic, written in python, the ‘frontend’ i.e. the interface, written in JS + React/CSS, and the ‘middleware’ the software that allows these two domains to communicate, as well as providing the required ‘runtime’ to execute the code. This portion is powered by the Electron framework.

# What is a daysheet
A “Daysheet”, or a daily staffing sheet, at the most basic level, is a one day schedule view that contains the current date and day of the week, all employees in the relevant scope and their shift start and end times. The employees are organized both by department role and shift start time.

# Why does this tool exist.
Prior to my workplace implementing this tool, it was a weekly ritual for a member of the frontline management staff in the relevant department to spend at least half an hour filling out seven daysheets by hand. This process involves scanning the schedule spreadsheet over and over, first picking out and typing all the names of employees on the relevant day, entering their name and shift hours into the daysheet, and ordering the employees by role and start time. The alternative, using Kronos to generate daysheets, produces an inferior product. Leading multiple managers to create their own daysheets in Excel instead."

This tool automates the process entirely. Additionally, the daysheets produced by this program are much richer with information than anything worth the effort of implementing by hand. There’s a lot of data in those schedules, and the output from this program takes advantage of it to provide actionable information.

# What are time Blocks
A ‘Time Block’ is a range of time of arbitrary duration and name. The application stores the time blocks you define, and then can then measure the total labor hours which ‘overlap’ with these ranges. For example, if I define a time block from 5am to 10am and I have three employees, Jeff who works from 5am to noon, Laura who works from 7am to 3pm, and Michelle who works from noon to 9pm. Jeff would contribute 5 hours (5am – 10am), Laura would contribute 3 hours (7am – 10am), and Michelle would contribute 0 hours, as her shift starts past 10am. In total, this time block would have a value of 8 labor hours.

>This can be implemented in a number of ways, depending on whats most useful to the manager and department inquestion. The time blocks tracked cold be >as simple as having one tracked block during a labor intensive time,like production at 5am - 8am in the bakery. Or it could be used to equally divide >the day to understand the ebband flow of labor coverage over time.

![The 'Time Blocks' managment menu.](https://raw.githubusercontent.com/emmatey/day-sheet-maker/refs/heads/react-ui/assets/readmeImages/timeBlocksEditMenu.png)
*The 'Time Blocks' managment menu.*

# What are ‘roles’ and how can I configure them?
Roles are the sub-categories of each department like ‘cashier’ vs ‘help desk’ vs ‘service leader’. Some departments utilize roles when making their schedules and some don’t. As a user of daysheet maker you have the option to configure a handful of roles related options.
##	1. “Raw name” vs “Display name” -
On the schedules from Kronos many roles will have “ugly” names like ‘Crt Str Assoc’ or ‘CashierEXP’. Because of this you’re able to configure a ‘display name’ of your choosing. This ‘display name’ will be what you see on the headers for each role’s subsection, as well as the labor trackers.
>You can also choose to assign many different ‘raw roles’ the same ‘display role’. For example, in the customer service department, by default, ‘SL >SelfScan’, and ‘Service Clerk’ are both given the ‘display role’ of “Service desk. This will group them together in the output, and count their hours in >the same labor trackers.
##	2. Role Order –
The order of the roles in the settings menu will mirror the order of the roles in your daysheet output. So if for example you want to put manager roles at the top of the page you can do that. What makes the most sense for you will vary by context. You can change the order of roles with the arrow buttons on the role configuration page.
##	3. Role Enable/Disable -
Each role also allows you to enable or disable its ‘labor tracker’ from your output. For example, if you don’t need metrics to track a specific role (e.g., if it’s very small and staffing is easily determined)." You can simply disable that role’s labor tracker to make the output cleaner. If every role is disabled “Daily Notes” will be inserted instead.

>**Note:** In the case of ‘department A’ having a member of ‘department B’ scheduled for a shift in ‘department A’, next to the relevant employee’s name >will be *"– (Native Role)"*. So, for example if a cashier is scheduled in the meat department for a day, on the meat department’s daysheet the cashier will >be listed as *First Last - (“Cashier”)*

![The menu to configure roles.](https://raw.githubusercontent.com/emmatey/day-sheet-maker/refs/heads/react-ui/assets/readmeImages/roleMapSettingsMenu.png)
*The menu to configure roles.*

# What are labor trackers
The labor tracker is just a collection of all the time blocks you’ve configured shown as a table ordered by start time. They can have as many elements as you have time blocks, and will be rendered by default on a per role basis in your output. However there’s also the option to condense all the per-role labor trackers into a unified table that tracks the entire department as one unit.

![Standard 'Labor Trackers' for a department with 4 roles.](https://raw.githubusercontent.com/emmatey/day-sheet-maker/refs/heads/react-ui/assets/readmeImages/laborTrackers.png)
*Standard 'Labor Trackers' for a department with 4 roles.*

!['Labor Trackers' for a department with 4 roles, and one disabled.](https://raw.githubusercontent.com/emmatey/day-sheet-maker/refs/heads/react-ui/assets/readmeImages/roleDisabledLaborTrackerExample.png)
*'Labor Trackers' for a department with 4 roles, and one disabled.*

!['Labor Trackers' where scope is shifted from per role to per department.](https://raw.githubusercontent.com/emmatey/day-sheet-maker/refs/heads/react-ui/assets/readmeImages/unifiedLaborTracker.png)
*'Labor Trackers' where scope is shifted from per role to per department.*

# What is ESH
ESH, or effective/estimated shopping hours is an online fulfillment department specific metric. It attempts to show, at a glance, how many labor hours per hour of shopping power the department will have. This is useful for comparing against the estimated labor required figure in the order management system’s dashboard.
With these two data points, anyone will easily be able to forecast a shortage, and in my personal experience I have used this metric to predict shortages hours in advance, before anyone else had noticed, and was able to rectify the situation before it got out of hand.
The metric ESH is derived by a simple formula. In any given hour ESH is calculated as..

>ESH/hour = (Total_labor_scheduled_per_hour) – (hourly_ESH_constant)

![A daysheet featuring the ESH table.](https://raw.githubusercontent.com/emmatey/day-sheet-maker/refs/heads/react-ui/assets/readmeImages/eshExample.png)
*A daysheet featuring the ESH table.*

The “ESH constant” is configurable by the user and can be changed for every hour. It is meant to represent time allotted for all activities that aren’t shopping. This could be the non-shopper role, it could be breaks, it could be the time that people take to set up between trips. The default settings were arrived at after surveying multiple people in the online fulfillment department and getting their opinions.
ESH can also be disabled entirely in favor of the time blocks system, or the “Daily Notes”.

![The menu to edit ESH constant.](https://raw.githubusercontent.com/emmatey/day-sheet-maker/refs/heads/react-ui/assets/readmeImages/eshEditMenu.png)
*The menu to edit ESH constant.*

# What do you mean by “Daily Notes”
In the event that every role is “disabled” in settings, or the daily notes override setting is enabled, in lieu of the ESH table, or time time blocks, a “Daily Notes” block is rendered instead. This is just free writing space and is available both as a fallback option, and as a preference for people who find more value in writing their own announcements by hand, which is understandable because the daysheets are typically seen by everyone multiple times per day.

!['Daily notes' example.](https://raw.githubusercontent.com/emmatey/day-sheet-maker/refs/heads/react-ui/assets/readmeImages/dailyNotesExample.png)
*'Daily notes' example.*

# Where is the output saved?
By default the program saves your output to a directory called "Daysheet Archive" located in the "Documents" directory of the current user. However, you can specify an arbitrary save location in the application settings.

![Save Location.](https://raw.githubusercontent.com/emmatey/day-sheet-maker/refs/heads/react-ui/assets/readmeImages/saveLocation.png)
*Save Location.*