SELECT
    A.sheet_Id AS 工单流水号,
    A.title AS 工单主题,
    A.main_City AS 地市,
    A.main_County AS 区县,
    CASE c.provincelevel
        WHEN '1' THEN '一级'
        WHEN '2' THEN '二级'
        WHEN '3' THEN '三级'
        WHEN '4' THEN '四级'
        WHEN '5' THEN '五级'
        WHEN '6' THEN '六级'
        WHEN '7' THEN '七级'
        WHEN '8' THEN '八级'
        ELSE c.provincelevel
        END AS 省内派单级别,
    A.main_Tenance_Group AS 维护班组,
    A.main_Tenance_Mode AS 维护方式,
    A.main_Tenance_Company AS 代维公司,
    A.main_Netsort_One AS 网络一级分类,
    A.main_Netsort_Two AS 网络二级分类,
    A.main_Netsort_Three AS 网络三级分类,
    A.sheet_Accept_Limit AS 受理时限,
    A.sheet_Complete_Limit AS 处理时限,
    -- 核心修改：工单状态映射为中文
    CASE A.status
        WHEN 'ACCEPTING' THEN '已受理'
        WHEN 'ARCHIVED' THEN '已归档'
        WHEN 'IN_PROGRESS' THEN '处理中'
        ELSE A.status
    END AS 工单状态,
    A.send_Time AS 派单时间,
    A.end_Time AS 归档时间,
    A.currently_Alarm_Fp AS 事件流水号,
    c.event_Id AS 事件编码,
    c.event_Name AS 事件名称,
    c.event_Level AS 事件级别,
    c.event_Type AS 事件类型,
    c.event_Happen_Time AS 事件发生时间,
    c.event_Found_Time AS 事件发现时间,
    c.event_Clean_Time AS 事件清除时间,
    c.related_Major AS 相关专业,
    c.trigger_Major AS 触发专业,
    c.root_Cause_Major AS 根因专业,
    c.fault_Root_Cause_Type AS 故障侧根因分类,
    c.root_Cause_Ne_Id AS 根因网元ID,
    c.root_Cause_Ne_Name AS 根因网元,
    c.root_Cause_Ne_Type AS 根因网元类型,
    c.root_Cause_Ne_Factory AS 根因网元厂家,
    c.root_Cause_Ne_Ip AS 根因网元IP,
    c.root_Cause_Longitude AS 根因网元经度,
    c.root_Cause_Latitude AS 根因网元纬度,
    c.trigger_Ne_Id AS 触发网元ID,
    c.trigger_Ne_Name AS 触发网元,
    c.trigger_Net_Type AS 触发网元类型,
    c.trigger_Ne_Factory AS 触发网元厂家,
    c.trigger_Ne_Ip AS 触发网元IP,
    c.trigger_Longitude AS 触发网元经度,
    c.trigger_Latitude AS 触发网元纬度,
    c.is_Effect_Business AS 是否影响业务,
    c.serve_Effect_Type AS 影响业务类型,
    c.event_Pretreatment AS 事件预处理情况,
    c.event_Location_Info AS 事件定界定,
    c.event_Effect AS 事件影响,
    c.wireless_Site_Type AS 无线站点类型,
    c.ci AS CI,
    c.business_Level AS 业务层级,
    c.machinery_Room AS 机房信息,
    c.machinery_User AS 机房长姓名,
    c.machinery_U_Phone AS 机房长联系电话,

    -- 遗留库申请相关信息
    legacy_apply.create_Time AS 最后一次入遗留库申请时间,
    legacy_approve.create_Time AS 最后一次入遗留库审批通过时间,
    '是' AS 最后一次入遗留库审批结果,
    legacy_approve.OPERATE_ROLE_ID AS 入遗留库审批通过人员角色,
    legacy_approve.OPERATE_DEPT_ID AS 入遗留库审批通过人员部门,
    legacy_approve.OPERATE_USER_ID AS 入遗留库审批通过人员,

    -- 遗留库申请JSON字段解析（MySQL兼容）
    JSON_UNQUOTE(JSON_EXTRACT(legacy_apply.CLASS_JSON, '$.expectedSolveTime')) AS 入遗留库通过预计解决时间,
    JSON_UNQUOTE(JSON_EXTRACT(legacy_apply.CLASS_JSON, '$.legacyReasonCategory')) AS 入遗留库原因类别,
    JSON_UNQUOTE(JSON_EXTRACT(legacy_apply.CLASS_JSON, '$.legacyReasonSubcategory')) AS 入遗留库原因细分,
    JSON_UNQUOTE(JSON_EXTRACT(legacy_apply.CLASS_JSON, '$.legacyApplicationReason')) AS 入遗留库申请理由,
    JSON_UNQUOTE(JSON_EXTRACT(legacy_apply.CLASS_JSON, '$.legacyEntryApprovalComment')) AS 入遗留库审批意见,

    d.link_Fault_Reason_Sort AS 故障原因分类,
    d.link_Fault_Cause_Subtype AS 故障原因细分,
    d.link_Fault_Desc AS 故障原因描述,
    d.link_Deal_Step AS 处理措施,
    d.link_Final_Equipment_Factory AS 最终设备厂家,
    d.link_If_Hidden_Danger AS 是否存在隐患,
    d.link_Hidden_Danger_Desc AS 隐患描述,

    b.sheet_Id AS 互调工单号,
    b.send_Time AS 互调工单号的派单时间,
    -- 修正时间计算逻辑：MySQL使用TIMESTAMPDIFF
    ROUND(TIMESTAMPDIFF(SECOND, b.create_Time, b.end_Time) / 3600.0, 4) AS 总故障历时,
    c.event_Happen_Time AS 互调工单号的事件发生时间,
    c.event_Clean_Time AS 互调工单号的事件清除时间,

    -- 关联子单数量
    (SELECT COUNT(*) FROM MW_ORDER_WORK_RELATED WHERE sheet_id = A.sheet_id) AS 关联子单数量

FROM MW_ORDER_WORK A
         LEFT JOIN MW_ORDER_WORK B
                   ON A.EVENT_NUMBER = B.EVENT_NUMBER
                       AND B.ORDER_TYPE = 'GENERAL_WORK_ORDER'
         LEFT JOIN MW_ORDER_PUBLIC_INCIDENT C
                   ON A.EVENT_NUMBER = C.EVENT_NUMBER
         LEFT JOIN MW_ORDER_CIRCULATE_INFO D
                   ON A.sheet_id = D.sheet_id
-- 获取最后一次遗留库申请记录
         LEFT JOIN (
    SELECT
        sheet_id,
        create_Time,
        CLASS_JSON,
        ROW_NUMBER() OVER (PARTITION BY sheet_id ORDER BY CREATE_TIME DESC) as rn
    FROM MW_ORDER_CIRCULATE
    WHERE OPERATE_TYPE IN ('T1_LEGACY_APPLICATION','T2_LEGACY_APPLICATION')
) legacy_apply
                   ON A.sheet_id = legacy_apply.sheet_id
                       AND legacy_apply.rn = 1
-- 获取最后一次遗留库审批通过记录
         LEFT JOIN (
    SELECT
        sheet_id,
        create_Time,
        OPERATE_ROLE_ID,
        OPERATE_DEPT_ID,
        OPERATE_USER_ID,
        ROW_NUMBER() OVER (PARTITION BY sheet_id ORDER BY CREATE_TIME DESC) as rn
    FROM MW_ORDER_CIRCULATE
    WHERE OPERATE_TYPE IN ('T1_LEGACY_APPROVED','T2_LEGACY_APPROVED')
) legacy_approve
                   ON A.sheet_id = legacy_approve.sheet_id
                       AND legacy_approve.rn = 1

WHERE A.EVENT_NUMBER IS NOT NULL
  AND A.STATUS NOT IN ('SHIELD', 'EXCEPTION', 'VOIDED', 'DRAFT', 'SUSPENDED')
  AND A.ORDER_TYPE = 'LEGACY_ORDER'
  AND A.LINK_EXCEPTION_LIBRARY_REASON_DESC IS NULL
  AND A.CREATE_TIME BETWEEN '2025-01-13 00:00:00' AND '2026-04-19 23:59:59'
  AND A.MAIN_CITY = '泉州市'
ORDER BY A.SEND_TIME DESC
