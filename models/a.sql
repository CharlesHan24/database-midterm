
select cand_prof.stu_id, stu_name, grade, contact, student_avg.avg_score from (select stu_id, avg(score) as avg_score
from evaluate   
group by stu_id) as student_avg right join cand_prof on student_avg.stu_id = cand_prof.stu_id