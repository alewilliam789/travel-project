SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
-- =============================================
-- Author:      Alex Williamson
-- Create Date: 08/15/2024
-- Description: Inserts the World Bank recognized regions from staging data

-- =============================================


CREATE PROCEDURE [dbo].[sp_InsertRegions]
AS
BEGIN
    -- SET NOCOUNT ON added to prevent extra result sets from
    -- interfering with SELECT statements.
    SET NOCOUNT ON;


    WITH CTE AS (
        SELECT stg.CountryCode,
        CASE 
            WHEN CHARINDEX('(',stg.CountryName) > 0 THEN SUBSTRING(stg.CountryName, 1, CHARINDEX('(',stg.CountryName)-2)
            WHEN CHARINDEX('SAR',stg.CountryName) > 0 THEN SUBSTRING(stg.CountryName,1,CHARINDEX('SAR',stg.CountryName)-1)
            ELSE stg.CountryName
        END as RegionName
        FROM TravelSTAGE.dbo.STAGE_NoFillArrival stg
        LEFT JOIN TravelDB.dbo.DIM_Countries dim
        ON dim.CCA3 = stg.CountryCode
        WHERE CountryID is null and stg.CountryCode NOT IN ('AFE', 'AFW','ARB','CEB','CSS','EAP','EAR','EAS','ECA','ECS','EMU','EUU','FCS','HIC','HPC','IBD',
        'IBT','IDA','IDB','IDX','INX','LAC','LCN','LDC','LIC','LMC','LMY','LTE','MEA','MIC','MNA','NAC','OED','OSS','PRE','PSS','PST','SAS','SSA','SSF','SST',
        'TEA','TEC','TLA','TMN','TSA','TSS','UMC','WLD')
    )

    MERGE INTO TravelDB.dbo.DIM_Regions targ
    USING(
        SELECT CTE.RegionName, CTE.CountryCode
        FROM CTE
        GROUP BY CTE.RegionName, CTE.CountryCode
    ) as src
    ON src.CountryCode = targ.CCA3
    WHEN NOT MATCHED
    THEN INSERT (RegionName, CCA3)
    VALUES (src.RegionName, src.CountryCode);
END
GO
