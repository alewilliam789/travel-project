SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
-- =============================================
-- Author:      Alex Williamson
-- Create Date: 08/15/2024
-- Description: Inserts the arrival data for regions

-- =============================================

CREATE PROCEDURE [dbo].[sp_InsertRegionArrivals]
AS
BEGIN
    -- SET NOCOUNT ON added to prevent extra result sets from
    -- interfering with SELECT statements.
    SET NOCOUNT ON;

    -- Get non-NULL TouristAmount Years for Regions with a lag to check if there are year gaps between data  
    WITH CTE AS( 
        SELECT dim.RegionID, dim.RegionName, arr.ArrivalYear, arr.TouristAmount, LAG(arr.ArrivalYear) OVER(PARTITION BY dim.RegionID ORDER BY ArrivalYear) as previous_year
        FROM TravelSTAGE.dbo.STAGE_NoFillArrival arr
        INNER JOIN dbo.DIM_Regions dim
        ON dim.CCA3 = arr.CountryCode
        WHERE arr.TouristAmount is not null
    ), 
    -- Get the years that are missing direct previous years 
    PREV AS (
        SELECT CTE.RegionID, CTE.RegionName, CTE.ArrivalYear,
            CASE 
                WHEN CTE.previous_year <> CTE.ArrivalYear -1 THEN NULL
                ELSE CTE.previous_year
            END AS prev
        FROM CTE
    -- Get the largest year with a NULL value
    ), MINWINDOW AS (
        SELECT PREV.RegionID,  PREV.RegionName, MAX(ArrivalYear) AS min_window
        FROM PREV
        WHERE prev is null
        GROUP BY RegionID, RegionName
    -- Get the largest non-NULL year
    ), MAXWINDOW AS (
        SELECT CTE.RegionID, CTE.RegionName, MAX(ArrivalYear) as max_window
        FROM CTE
        GROUP BY CTE.RegionID, CTE.RegionName
    -- Get the final table to constrain the window for a region
    ), FINAL AS (
            SELECT MINWINDOW.RegionID, min_window, max_window
            FROM MINWINDOW
            INNER JOIN MAXWINDOW
            ON MINWINDOW.RegionID = MAXWINDOW.RegionID
    )


    MERGE INTO TravelDB.dbo.FACT_RegionArrivals targ
    USING(
        SELECT dim.RegionID, STAGE_NoFillArrival.CountryCode, STAGE_NoFillArrival.ArrivalYear, STAGE_NoFillArrival.TouristAmount
        FROM TravelSTAGE.dbo.STAGE_NoFillArrival
        INNER JOIN DIM_Regions dim
        ON TravelSTAGE.dbo.STAGE_NoFillArrival.CountryCode = dim.CCA3
        INNER JOIN FINAL 
        ON dim.RegionID = FINAL.RegionID
        WHERE STAGE_NoFillArrival.ArrivalYear BETWEEN FINAL.min_window AND FINAL.max_window
    ) as src
    ON src.RegionID = targ.RegionID
    AND src.ArrivalYear = targ.ArrivalYear
    WHEN NOT MATCHED
    THEN INSERT (RegionID, ArrivalYear, TouristAmount)
    VALUES (src.RegionID, src.ArrivalYear, src.TouristAmount);
END
GO
