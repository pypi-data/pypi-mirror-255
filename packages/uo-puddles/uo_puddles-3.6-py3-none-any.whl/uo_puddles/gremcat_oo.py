import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime
import random
import pandas as pd
from getpass import getpass

'''
class Commit(models.Model):
    hash = models.CharField(max_length=128)
    datetime = models.DateTimeField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    message = models.TextField()
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    branch = models.TextField()

    class Meta:
        db_table = 'commit'
        ordering = ['id']
        verbose_name = 'commit'
        verbose_name_plural ='commits'

    def __str__(self):
        return f'Commit {self.hash}'
'''
class Commit():
  def __init__(self, commit_tuple) -> None:
    self.id = commit_tuple[0]        #e.g., 322121
    self.hash = commit_tuple[1]      #e.g., 'e45385dc57b6c33a2e987ed9e5cde29f790048da'
    self.datetime = commit_tuple[2]  #e.g., datetime.datetime(2022, 5, 6, 10, 31, 40)
    self.message = commit_tuple[3]
    self.branch = commit_tuple[4]    #e.g., '* main\n  remotes/origin/HEAD -> origin/main\n  remotes/origin/main\n'
    self.author = commit_tuple[5]    #e.g., 2246
    self.project = commit_tuple[6]   #e.g., 30

    #added field not in db
    branch_list = self.branch.strip().split('\n')
    self.short_branch = branch_list[-1].strip().replace('remotes/origin/', '')  #main

  def as_dict(self):
    return self.__dict__

def all_commits(project_id, the_cursor) -> list:
  commits_list = []
  query = f"select * from commit where project_id={project_id}"  #30=anl_test_repo
  the_cursor.execute(query)
  commit_list = the_cursor.fetchall()

  commit_objects = [Commit(ctup) for ctup in commit_list]  #convert tuples to objects

  return commit_objects

#project_commits = all_commits(30)  #30 = anl_test_repo

def get_commits_for_branch(commit_list, branch):
  return [commit for commit in commit_list if commit.short_branch==branch]

'''
class Diff(models.Model):
    file_path = models.FilePathField(max_length=256)
    language = models.CharField(max_length=64)
    body = models.TextField()
    header = models.TextField(null=True)
    commit = models.ForeignKey(Commit, on_delete=models.CASCADE)

    class Meta:
        db_table = 'diff'
        ordering = ['id']
        verbose_name = 'diff'
        verbose_name_plural ='diffs'

    def __str__(self):
        return f'Diff {self.file_path}'
'''
class Diff():
  def __init__(self, diff_tuple) -> None:
    self.id = diff_tuple[0]        #e.g., 1362217
    self.file_path = diff_tuple[1]  #e.g., 'folder1/arithmetic.py'
    self.language = diff_tuple[2]  #e.g., 'PLACEHOLDER'
    self.body = diff_tuple[3]      #e.g., '@@ -1,5 +1,5 @@\n \n-\n+#Adding this comment to just test committing and diff data\n def sub(x,y):\n   """\n   Return the subtraction of two numbers::'
    self.commit = diff_tuple[4]    #e.g.,  322121
    self.header = diff_tuple[5]    #e.g.,  'diff --git a/folder1/arithmetic.py b/folder1/arithmetic.pyindex 3966a24..f65f01d 100644--- a/folder1/arithmetic.py+++ b/folder1/arithmetic.py@@ -1,5 +1,5 @@')

  def as_dict(self):
    return self.__dict__

def compute_chars_changed(diff_body):
  crude_list = diff_body.split('\n')
  chars_changed = sum([len(item)-1 for item in crude_list if item.strip().startswith('-') or item.strip().startswith('+')])
  return chars_changed

def get_diffs_for_commit(commit_id, the_cursor):
  diffs_list = []
  query = f"select * from diff where commit_id={commit_id}"
  the_cursor.execute(query)
  diffs_list = the_cursor.fetchall()

  diff_objects = [Diff(dtup) for dtup in diffs_list]  #convert tuples to objects

  return diff_objects

def get_branches(commit_list, ignore_list) -> list:
  all_branches = [commit.short_branch for commit in commit_list]
  unique_branches = list(set(all_branches) - set(ignore_list))  #trim down to unique set excluding those branches in ignore_list
  return unique_branches

def commits_for_branch(commits_list, branch):
  branch_commits = [commit for commit in commits_list if commit.short_branch==branch]
  return branch_commits

## Compute LOC for a branch per day for a time span

def branch_loc(project_id, branch, start, stop, the_cursor) -> dict:
  commits_list = [commit for commit in all_commits(project_id, the_cursor)]
  branch_commits = commits_for_branch(commits_list, branch)
  loc_by_date = dict()
  for commit in branch_commits:
    if commit.datetime < start or commit.datetime > stop: continue  #out of date range
    diffs = get_diffs_for_commit(commit.id, the_cursor)
    loc = sum([compute_chars_changed(d.body) for d in diffs])
    date = commit.datetime  #remains in datetime form
    short_date = datetime.datetime(date.year, date.month, date.day)
    if short_date in loc_by_date:
      loc_by_date[short_date] += loc
    else:
      loc_by_date[short_date] = loc

  return loc_by_date

def plot_timeline(project_id, branch, start, stop, the_cursor):
  loc_by_date = branch_loc(project_id, branch, start, stop, the_cursor)
  time = mdates.drange(start, stop, datetime.timedelta(days=1))

  # Plot things...
  fig = plt.figure(figsize=(20, 6))
  plt.title(f'LOC for branch {branch} by date range')
  plt.ylabel('Total characters added and deleted')
  plt.grid()
  plt.yscale("log")

  loc_timeline = []
  current_date = start
  while(current_date<stop):
    if current_date in loc_by_date:
      loc_timeline.append(loc_by_date[current_date])
    else:
      loc_timeline.append(0)  #nothing done on current_date
    current_date += datetime.timedelta(days=1)

  plt.plot_date(time, loc_timeline, 'b-')
  #plt.plot_date(time, loc2, 'r-')  could also plot another branch on same graph

  fig.autofmt_xdate()
  plt.show()
