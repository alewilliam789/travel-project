SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
-- =============================================
-- Author:      Alex Williamson
-- Create Date: 08/05/2024
-- Description: Inserts the newest arrival data

-- Edit: Changed the Arrivals to a Fact Table
-- =============================================


CREATE PROCEDURE [dbo].[sp_InsertCountryArrivals]
AS
BEGIN
    -- SET NOCOUNT ON added to prevent extra result sets from
    -- interfering with SELECT statements.
    SET NOCOUNT ON

    -- Insert statements for procedure here
    MERGE INTO TravelDB.dbo.FACT_CountryArrivals targ
    USING(
        SELECT *
        FROM TravelSTAGE.dbo.STAGE_NoFillArrival stg
        INNER JOIN dbo.DIM_Countries dim
        ON dim.CCA3 = stg.CountryCode
    ) as src
    ON src.CountryCode = targ.CountryCode
    AND src.ArrivalYear = targ.ArrivalYear
    WHEN NOT MATCHED
    THEN INSERT (CountryID, CountryCode, ArrivalYear, TouristAmount)
    VALUES (src.CountryID, src.CountryCode, src.ArrivalYear, src.TouristAmount);
END
GO
