import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime
import random
import pandas as pd
import numpy as np
from getpass import getpass

import builtins
import types

pd.set_option('mode.chained_assignment', None)  #https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#returning-a-view-versus-a-copy

#use: @up_no_globals(globals())  #globals is function that returns *current* globals as dict
#DANGER DANGER: this fails on forward refs. Assumes helper functions all defined before main function. If not will get spurious error.
def up_no_globals(gfn:dict):

  def wrap(f):
    new_globals = {'__builtins__': builtins} 
    # removing keys from globals() storing global values in old_globals
    for key, val in gfn.items():
      if  callable(val):
          new_globals[key] = val
    new_f = types.FunctionType(f.__code__, globals=new_globals, argdefs=f.__defaults__)
    new_f.__annotations__ = f.__annotations__ # for some reason annotations aren't copied over
    return new_f

  return wrap


def get_commits(proj_name, cursor):
    query = f'''
    select proj.id as project_id, proj.name as project_name,
	   proj.last_updated as project_last_updated, proj.source_url as project_source_url,
       proj.fork_of_id as project_fork_of_id, proj.child_of_id as project_child_of_id,
       c.id as commit_id, c.hash as commit_sha, c.datetime as commit_datetime, c.message as commit_message,
       c.branch as commit_branch, a.id as author_id, a.username as author_username, a.name as author_name,
       a.email as author_email, a.url as author_url, d.file_path as diff_file_path, d.language as diff_language,
       d.body as diff_body
    from project proj join commit c on(proj.id=c.project_id) join author a on(c.author_id=a.id)
        join diff d on (d.commit_id=c.id)
    where proj.name = '{proj_name}'
    '''
    cursor.execute(query)
    data = cursor.fetchall()
    cols = [col[0] for col in cursor.description]
    df = pd.DataFrame(data, columns=cols)

    def shorten(branch_list):
      short_list = []
      for branch in branch_list:
        b = branch.strip().split('\n')
        shortie = b[-1].strip().replace('remotes/origin/', '')  #main
        short_list.append(shortie)
      return short_list

    df['short_branch'] = shorten(df.commit_branch.to_list())
    return df

def get_prs(proj_name, cursor):
    query = f'''
    select proj.id as project_id, proj.name as project_name,
	   proj.last_updated as project_last_updated, proj.source_url as project_source_url,
       proj.fork_of_id as project_fork_of_id, proj.child_of_id as project_child_of_id,
       p.id as pr_id, p.title as pr_title, p.description as pr_description, p.updated_at as pr_updated_at, p.created_at pr_created_at,
       p.locked as pr_locked, p.url as pr_url, p.number as pr_number, p.state as pr_state, p.merged_at as pr_merged_at,
       p.head_sha as pr_head_sha, a1.id as pr_author_id, a1.username as pr_author_username, a1.email as pr_author_email,
       a1.name as pr_author_name, a1.url as pr_author_url, m.id as milestone_id, m.title as milestone_title,
       m.description as milestone_description, m.state as milestone_state, m.due_on as milestone_due_on,
       m.created_at as milestone_created_at, m.updated_at as milestone_updated_at, l.id as pr_label_id, l.name as pr_label,
       a2.id as pr_assignee_id, a2.name as pr_assignee_name, a2.url as pr_assignee_url, a2.username as pr_assignee_username, a2.email as pr_assignee_email,
       ct.id as pr_sha_id, ct.sha as pr_sha, comm.id as pr_comment_id, comm.created_at as pr_comment_created_at, comm.updated_at as pr_comment_updated_at, comm.body as pr_comment_body,
	   a3.id as pr_comment_author_id, a3.name as pr_comment_author_name, a3.url as pr_comment_author_url, a3.username as pr_comment_author_username, a3.email as pr_comment_author_email,
       it.url as linked_issue_url
    from project proj join pr p on(p.project_id = proj.id) join author a1 on(a1.id=p.author_id) 
	   left join milestone m on(m.pr_id=p.id) left join pr_has_label phl on(phl.pr_id=p.id) left join label l on(l.id=phl.label_id)
       left join pr_has_assignee pha on(pha.pr_id=p.id) left join author a2 on(a2.id=pha.assignee_id)
       left join pr_has_commit phc on(phc.pr_id=p.id) left join commit_tag ct on(ct.id=phc.commit_id)
       left join comment comm on(comm.pr_id=p.id) left join author a3 on(a3.id=comm.author_id)
       left join pr_has_issue phi on(phi.pr_id=p.id) left join issue_tag it on(it.id=phi.issue_id)
    where proj.name = '{proj_name}';
    '''
    cursor.execute(query)
    data = cursor.fetchall()
    cols = [col[0] for col in cursor.description]
    return pd.DataFrame(data, columns=cols)
    

def get_issues(proj_name, cursor):
    query = f'''
    select proj.id as project_id, proj.name as project_name,
	   proj.last_updated as project_last_updated, proj.source_url as project_source_url,
       proj.fork_of_id as project_fork_of_id, proj.child_of_id as project_child_of_id,
	   i.id as issue_id, i.title as issue_title, i.description as issue_description, i.created_at as issue_created_at,
	   i.updated_at as issue_updated_at, i.closed_at as issue_closed_at, i.locked as issue_locked, i.state as issue_state,
       i.url as issue_url, i.number as issue_number, a1.username as issue_author_username, a1.email as issue_author_email,
       a1.name as issue_author_name, a1.url as issue_author_url, m.id as milestone_id, m.title as milestone_title,
       m.description as milestone_description, m.state as milestone_state, m.due_on as milestone_due_on,
       m.created_at as milestone_created_at, m.updated_at as milestone_updated_at, l.id as issue_label_id, l.name as issue_label,
       a2.id as issue_assignee_id, a2.name as issue_assignee_name, a2.url as issue_assignee_url, a2.username as issue_assignee_username, a2.email as issue_assignee_email,
       comm.id as issue_comment_id, comm.created_at as issue_comment_created_at, comm.updated_at as issue_comment_updated_at, comm.body as issue_comment_body,
	   a3.id as issue_comment_author_id, a3.name as issue_comment_author_name, a3.url as issue_comment_author_url, a3.username as issue_comment_author_username, a3.email as issue_comment_author_email
    from project proj join issue i on(proj.id=i.project_id) join author a1 on(a1.id=i.author_id) 
         left join milestone m on(m.issue_id=i.id) left join issue_has_label ihl on(ihl.issue_id=i.id) 
         left join label l on(l.id=ihl.label_id) left join issue_has_assignee iha on(iha.issue_id=i.id)
         left join author a2 on(iha.assignee_id=a2.id) left join comment comm on(comm.issue_id=i.id) left join author a3 on(a3.id=comm.author_id)
    where proj.name = '{proj_name}';'''
    cursor.execute(query)
    data = cursor.fetchall()
    cols = [col[0] for col in cursor.description]
    return pd.DataFrame(data, columns=cols)

def get_events(proj_name, cursor):
    query =f'''
    select p.id as project_id, p.source_url as project_url, p.name as project_name, p.last_updated as project_last_updated,
	   e.id as event_id, e.api_id as event_api_id, e.type as event_type, e.public as event_public, e.created_at as event_created_at,
       ea.id as event_actor_id, ea.actor_id as event_actor_api_id, ea.login as event_actor_login, ea.url as event_actor_url, 
       ea.avatar_url as event_actor_avatar_url, ea.gravatar_id as event_actor_gravatar_id,
       eo.id as event_org_id, eo.org_id as event_org_api_id, eo.login as event_org_login, eo.url as event_org_url, 
       eo.avatar_url as event_org_avatar_url, eo.gravatar_id as event_org_gravatar_id,
       er.id as event_repo_id, er.repo_id as event_repo_api_id, er.name as event_repo_name, er.url as event_repo_url,
       ep.id as event_payload_id, ep.action as event_payload_action, ep.ref as event_payload_ref, ep.ref_type as event_payload_ref_type,
       ep.master_branch as event_payload_master_branch,	ep.description as event_payload_description, ep.forkee_url as event_payload_forkee_url,
       ep.issue_url as event_payload_issue_url, ep.comment_url as event_payload_comment_url, ep.member_login as event_payload_member_login, 
       ep.pr_number as event_payload_pr_number,	ep.pr_url as event_payload_pr_url, ep.pr_review_url as event_payload_pr_review_url,	
       ep.push_id as event_payload_push_id,	ep.size as event_payload_size, ep.distinct_size as event_payload_distinct_size,	
       ep.head_sha as event_payload_head_sha, ep.before_sha as event_payload_before_sha, ep.release_url as event_payload_release_url,
       ep.effective_date as event_payload_effective_date, epage.id as event_page_id, epage.name as event_page_name, epage.title as event_page_title,
       epage.action as event_page_action, epage.sha as event_page_sha, epage.url event_page_url
    from project p join event e on(p.id=e.project_id) join event_actor ea on(e.actor_id=ea.id) join event_org eo on(e.org_id=eo.id)
			   join event_repo er on(e.repo_id=er.id) join event_payload ep on(e.payload_id=ep.id) left join event_has_page ehp on(ehp.payload_id=ep.id)
               left join event_page epage on (ehp.page_id=epage.id)
    where p.name = '{proj_name}';'''
    cursor.execute(query)
    data = cursor.fetchall()
    cols = [col[0] for col in cursor.description]
    return pd.DataFrame(data, columns=cols)

@up_no_globals(globals())
def view_event_history(event_df, first=100):
    payload_cols = [col for col in event_df if col.startswith('event_payload')]
    for i, (_, row) in enumerate(event_df.sort_values('event_created_at', ascending=False).iterrows()):
        if i == first:
            break 
        print(row['event_id'], row['event_type'], row['event_created_at'])
        for col in payload_cols:
            if row[col] and not pd.isnull(row[col]):
                print(f'\t{col}: {row[col]}')
        print('-'*80)
	
@up_no_globals(globals())
def list_open_issues(issue_df):
    issue_df = issue_df.drop_duplicates(subset=['issue_label_id'])
    
    issue_df = issue_df.query('issue_state == "OPEN"')
    issue_df = issue_df[['issue_id', 'issue_title', 'issue_description', 'issue_label',
             'issue_author_username', 'issue_author_email', 'issue_author_name', 'issue_author_url',
             'issue_assignee_username', 'issue_assignee_email', 'issue_assignee_name', 'issue_assignee_url']]
    issue_df['infer_bug'] = 'bug' in issue_df['issue_title'].str.lower() or 'bug' in issue_df['issue_description'].str.lower()
    issue_df = issue_df.reset_index(drop=True)
    return issue_df

@up_no_globals(globals())
def find_linked_pr_info(pr_df, commit_df, issue_df, pr_url):
    df = pr_df.query(f'pr_url == "{pr_url}"')
    linked_shas = df.pr_sha.unique()
    linked_commits_df = commit_df.query('commit_sha in @linked_shas')
    linked_issues = df.linked_issue_url.unique()
    linked_issues_df = issue_df.query('issue_url in @linked_issues')
    return (linked_commits_df, linked_issues_df)
