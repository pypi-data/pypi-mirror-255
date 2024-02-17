SELECT 
board.id,
board.name as board,
board.description as board_desc,
board.url as board_url,
CONVERT(DATETIME, board.date_last_activity, 127) as board_last_activity,
list.name as list_name,
card.id as card_id,
card.name as card_name,
card.[desc] as card_desc,
DATEADD(SECOND, CONVERT(BIGINT, CONVERT(VARBINARY, '0x' + SUBSTRING(card.id, 1, 8), 1)), '19700101') as card_creation_date,
CONVERT(DATETIME, card.[start], 127) as card_start_date,
CONVERT(DATETIME, card.due, 127) as card_due_date,
CONVERT(DATETIME, card.date_last_activity, 127) as card_last_activity,
card.url as card_url,
ISNULL(ch.chapter,'Chapter NO especificado') as card_chapter, 
ISNULL(obp.obp_name, 'OBP NO especificado') as card_obp, 
ISNULL(div.division, 'División NO especificada') as card_division,
ISNULL(t.type ,'Tipo NO especificado') as card_type,
ISNULL(u.id, 'zz - na') as card_member_id,
ISNULL(u.fullname, 'zz - na') as card_member_fullname,
ISNULL(u.username, 'zz - na') as card_member_username
from (select * from [LATAM_AR].[trello].[MAE_Board] where id='618d68bc07ac868259356173') board
--Prefiltro solo las listas que interesan por Id
inner join (select * from [LATAM_AR].trello.MAE_List where active_in_trello=1 
			and id in ('618d68bc07ac868259356176','618d68bc07ac868259356177','618d68bc07ac868259356179',
			'618d68bc07ac86825935617a','618d68d95716f1680f6f4a6c','618e85290bc37a8502925155','6509ceecf62e03d11cfdfdba')
			) as list on list.idBoard=board.id
inner join (select * from [LATAM_AR].trello.MAE_Card where active_in_trello=1) as card on list.id=card.id_list
left join (select l.id as id, cl.id_card as card_id, REPLACE([name],'DIVISIÓN_','') as division 
			from [LATAM_AR].trello.REL_CardLabel cl
			inner join [LATAM_AR].trello.MAE_Label l on l.id=cl.id_label
			where cl.active_in_trello=1 and [name] like 'DIVISIÓN_%') as div on div.card_id=card.id
left join (select l.id, cl.id_card as card_id, REPLACE([name],'CHAPTER_','') as chapter 
			from [LATAM_AR].trello.REL_CardLabel cl
			inner join [LATAM_AR].trello.MAE_Label l on l.id=cl.id_label
			where cl.active_in_trello=1 and [name] like 'CHAPTER_%') as ch on ch.card_id=card.id
left join (select l.id, cl.id_card as card_id, REPLACE([name],'OBP_','') as obp_name 
			from [LATAM_AR].trello.REL_CardLabel cl
			inner join [LATAM_AR].trello.MAE_Label l on l.id=cl.id_label
			where cl.active_in_trello=1 and [name] like 'OBP_%') as obp on obp.card_id=card.id
left join (select l.id, cl.id_card as card_id, REPLACE([name],'TIPO_','') as type 
			from [LATAM_AR].trello.REL_CardLabel cl
			inner join [LATAM_AR].trello.MAE_Label l on l.id=cl.id_label
			where cl.active_in_trello=1 and [name] like 'TIPO_%') as t on t.card_id=card.id
left join (select * from [LATAM_AR].trello.REL_CardMembership where active_in_trello=1) as cmbshp on cmbshp.id_card=card.id
left join (select id, username,
				--Lamentablemente en Trello el fullname viene así. No me quedó otra que hacer esta porquería.
				--Pido perdón.
				case when full_name='fernas45' then 'Sara Fernandez'
				when full_name='Walter'then 'Walter Villar' else full_name end as fullname 
			from [LATAM_AR].trello.MAE_User where active_in_trello=1) as u on u.id=cmbshp.id_member