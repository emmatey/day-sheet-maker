<p>
![Document header](https://raw.githubusercontent.com/emmatey/day-sheet-maker/refs/heads/react-ui/assets/readmeImages/documentHeader.png)
</p>
Daysheet maker is a bespoke utility for a specific workplace and task. Its primary, and only function is to convert **Kronos schedules**, automatically generated for retail managers at the relevant business, and transform them into “Daysheets”.

## Quick Start
**This tool only works on Windows.**
1. Go to the [Releases page](https://github.com/emmatey/day-sheet-maker/releases).  
2. Download the latest installer: *DaySheetMaker-Setup-x.x.x.exe*.  
3. Run the file — installation is automated and only takes a moment.
4. Have your Kronos schedule spreadsheet ready for import. (.XLXS or .CSV only, no .PDFs!)

--- 

## What is a daysheet
A “Daysheet,” or daily staffing sheet, is a one-day schedule view for a specific department. It shows the date, day of the week, all employees in that department, and their shift start and end times.

## Why does this tool exist
It was a weekly ritual for a member of the frontline management staff in the relevant department to spend at least half an hour filling out seven daysheets by hand. This process involves scanning the schedule spreadsheet over and over; first picking out and typing all the names of employees on the relevant day, entering their name and shift hours into the daysheet, and ordering employees by role and start time. The alternative, using Kronos to generate daysheets, produces an inferior product. Leading multiple managers to manually create their own daysheets in Excel instead. 

This tool automates the process entirely. Additionally, the daysheets produced by this program are much richer with information than anything worth the effort of implementing by hand. There’s a lot of data in those schedules, and the output from this program takes advantage of it to provide actionable information.

## Tech Stack
This tool is composed of three sections, the ‘back-end’ processing logic, written in **Python**, the ‘front-end’ i.e. the interface, written in **JS + React/CSS**, and the ‘middleware’ the software that allows these two domains to communicate, the **Electron framework**.

---

# 1. How to Configure and Utilize Roles
Roles are the specific job categories within your department, such as 'cashier' or 'service leader.' They determine how your Daysheet is organized. The DaySheet Maker gives you complete control over how these roles are presented and tracked.

## A. Raw Name vs. Display Name: Grouping and Cleanup
The schedules exported from Kronos often contain abbreviated or "ugly" job titles, called Raw Names (e.g., 'Crt Str Assoc' or 'CashierEXP').
Your configuration allows you to map these raw names to a cleaner, user-friendly Display Name.
- Cleanup: The Display Name is what appears on your final Daysheet output and as the header for each role's subsection and Labor Tracker.
- Grouping: You can assign multiple Raw Names to the same Display Name. For example, you might map both 'SL SelfScan' and 'Service Clerk' to the single Display Name, "Service Desk." This groups them together on the output and consolidates their labor hours into a single tracker.

## B. Role Order
The list order in the settings menu will be mirrored exactly in your final output (e.g., placing Manager roles at the top).

## C. Labor Tracker Enable/Disable
Each configured role has an associated Labor Tracker (metrics for time blocks). If a role is very small or you don't need detailed staffing metrics for it, you can simply disable its Labor Tracker to keep your output cleaner. If all role trackers are disabled, the program will automatically substitute the tracking section with the "Daily Notes" block instead.
<p>
![The menu to configure roles.](https://raw.githubusercontent.com/emmatey/day-sheet-maker/refs/heads/react-ui/assets/readmeImages/roleMapSettingsMenu.png)
</p>
*The menu to configure roles.*
# 2. What are time blocks
A ‘Time Block’ is a range of time of arbitrary duration and name. The application stores the time blocks you define, and then can then measure the total labor hours which ‘overlap’ with these ranges. For example, if I define a time block from 5am to 10am and I have three employees, Jeff who works from 5am to noon, Laura who works from 7am to 3pm, and Michelle who works from noon to 9pm. Jeff would contribute 5 hours (5am – 10am), Laura would contribute 3 hours (7am – 10am), and Michelle would contribute 0 hours, as her shift starts past 10am. In total, this time block would have a value of 8 labor hours.

>This can be implemented in a number of ways, depending on what's most useful to the manager and department in question. The time blocks tracked could be as simple as having one tracked block during a labor intensive time,like production from 5am - 8am in the bakery. Or it could be used to equally divide the day to understand the ebb and flow of labor coverage over time.
<p>
![The 'Time Blocks' management menu.](https://raw.githubusercontent.com/emmatey/day-sheet-maker/refs/heads/react-ui/assets/readmeImages/timeBlocksEditMenu.png)
</p>
*The 'Time Blocks' management menu.*

# 3. What are labor trackers? (The Output of Roles and Time Blocks)
The labor tracker is just a collection of all the time blocks you’ve configured shown as a table ordered by start time. They can have as many elements as you have time blocks, and will be rendered by default on a per role basis in your output. However there’s also the option to condense all the per-role labor trackers into a unified table that tracks the entire department as one unit.
<p>
![Standard 'Labor Trackers' for a department with 4 roles.](https://raw.githubusercontent.com/emmatey/day-sheet-maker/refs/heads/react-ui/assets/readmeImages/laborTrackers.png)
</p>
*Standard 'Labor Trackers' for a department with 4 roles.*
<p>
!['Labor Trackers' for a department with 4 roles, and one disabled.](https://raw.githubusercontent.com/emmatey/day-sheet-maker/refs/heads/react-ui/assets/readmeImages/roleDisabledLaborTrackerExample.png)
</p>
*'Labor Trackers' for a department with 4 roles, and one disabled.*
<p>
!['Labor Trackers' where scope is shifted from per role to per department.](https://raw.githubusercontent.com/emmatey/day-sheet-maker/refs/heads/react-ui/assets/readmeImages/unifiedLaborTracker.png)
</p>
*'Labor Trackers' where scope is shifted from per role to per department.*

# 4. What is ESH
ESH, or effective/estimated shopping hours is an online fulfillment department specific metric. It attempts to show, at a glance, how many labor hours per hour of shopping power the department will have. This is useful for comparing against the estimated labor required figure in the order management system dashboard.
With these two data points, anyone will easily be able to forecast a labor shortage.

The metric ESH is derived by a simple formula: the Total Scheduled Labor per Hour minus a configurable Hourly ESH Constant.

$$\text{ESH/hour} = (\text{Total\_labor\_scheduled\_per\_hour}) - (\text{hourly\_ESH\_constant})$$
<p>
![A daysheet featuring the ESH table.](https://raw.githubusercontent.com/emmatey/day-sheet-maker/refs/heads/react-ui/assets/readmeImages/eshExample.png)
</p>
*A daysheet featuring the ESH table.*

The “ESH constant” is configurable by the user and can be changed for every hour. It is meant to represent time allotted for all activities that aren’t shopping. This could be the non-shopper role, it could be breaks, it could be the time that people take to set up between trips. The default settings were arrived at after surveying multiple people in the online fulfillment department and getting their opinions.
ESH can also be disabled entirely in favor of the time blocks system, or the “Daily Notes”.
<p>
![The menu to edit ESH constant.](https://raw.githubusercontent.com/emmatey/day-sheet-maker/refs/heads/react-ui/assets/readmeImages/eshEditMenu.png)
</p>
*The menu to edit ESH constant.*

# 5. What do you mean by “Daily Notes”
In the event that every role is “disabled” in settings, or the daily notes override setting is enabled, in lieu of the ESH table, or time blocks, a “Daily Notes” block is rendered instead. This is just free writing space and is available both as a fallback option, and as a preference for people who find more value in writing their own announcements by hand, which is understandable because the daysheets are typically seen by everyone multiple times per day.
<p>
!['Daily notes' example.](https://raw.githubusercontent.com/emmatey/day-sheet-maker/refs/heads/react-ui/assets/readmeImages/dailyNotesExample.png)
</p>
*'Daily notes' example.*

# 6. Where is the output saved?
By default the program saves your output to a directory called "Daysheet Archive" located in the "Documents" directory of the current user. However, you can specify an arbitrary save location in the application settings.
<p>
![Save Location.](https://raw.githubusercontent.com/emmatey/day-sheet-maker/refs/heads/react-ui/assets/readmeImages/saveLocation.png)
</p>
*Save Location.*
