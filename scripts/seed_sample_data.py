#!/usr/bin/env python3
"""
Generate realistic sample recall data for testing the site generator.
Run this when you can't hit the CPSC API (sandbox, offline, etc.)
"""
import json
from pathlib import Path
from datetime import datetime, timedelta
import random

DATA_DIR = Path(__file__).parent.parent / "data"

SAMPLE_RECALLS = [
    {
        "RecallNumber": "25-051",
        "RecallDate": "2025-03-15",
        "Title": "Graco Recalls Lightweight Strollers Due to Fall Hazard",
        "URL": "https://www.cpsc.gov/Recalls/2025/graco-recalls-lightweight-strollers",
        "Description": "The stroller's hinge can partially release during use, posing a fall hazard to children.",
        "ConsumerContact": "Graco at 800-345-4109 or www.gracobaby.com",
        "Products": [{"Name": "Graco NimbleLite Stroller", "Description": "Lightweight folding stroller with canopy and storage basket. Model numbers GL2024A and GL2024B printed on a label on the stroller frame.", "Type": "Strollers", "NumberOfUnits": "85,000"}],
        "Hazards": [{"Name": "The stroller's hinge mechanism can partially release during folding and unfolding, posing a fall hazard to children in the stroller.", "HazardType": "Fall"}],
        "Remedies": [{"Name": "Consumers should immediately stop using the recalled strollers and contact Graco for a free repair kit."}],
        "Manufacturers": [{"Name": "Graco Children's Products Inc."}],
        "ManufacturerCountries": [{"Country": "China"}],
        "Images": [{"URL": "https://www.cpsc.gov/s3fs-public/styles/recall_image/public/stroller-sample.jpg"}],
        "Injuries": [{"Name": "Graco has received 12 reports of the hinge releasing. No injuries reported."}],
        "_category": "strollers"
    },
    {
        "RecallNumber": "25-043",
        "RecallDate": "2025-03-01",
        "Title": "Fisher-Price Recalls Infant Swings Due to Entrapment Hazard",
        "URL": "https://www.cpsc.gov/Recalls/2025/fisher-price-recalls-infant-swings",
        "Description": "Infants can become entrapped between the seat and tray.",
        "ConsumerContact": "Fisher-Price at 800-432-5437 or www.fisher-price.com",
        "Products": [{"Name": "Fisher-Price Soothe & Swing", "Description": "Battery-operated infant swing with 6 swing speeds and music. Model FP-SW2023 printed on the bottom of the base.", "Type": "Infant Swings and Bouncers", "NumberOfUnits": "42,000"}],
        "Hazards": [{"Name": "Infants who are not restrained in the swing can move into a position between the seat pad and plastic tray, posing an entrapment hazard.", "HazardType": "Entrapment"}],
        "Remedies": [{"Name": "Consumers should immediately stop using the swing without the harness buckled and contact Fisher-Price for updated harness instructions."}],
        "Manufacturers": [{"Name": "Mattel Inc."}],
        "ManufacturerCountries": [{"Country": "China"}],
        "Images": [],
        "Injuries": [{"Name": "Fisher-Price received 5 reports of infants becoming partially entrapped. No injuries."}],
        "_category": "swings-bouncers"
    },
    {
        "RecallNumber": "25-038",
        "RecallDate": "2025-02-20",
        "Title": "Dream On Me Recalls Cribs Due to Entrapment and Suffocation Hazards",
        "URL": "https://www.cpsc.gov/Recalls/2025/dream-on-me-recalls-cribs",
        "Description": "Crib slats can loosen and detach creating gaps.",
        "ConsumerContact": "Dream On Me at 877-201-4738 or www.dreamonme.com",
        "Products": [{"Name": "Dream On Me Synergy 5-in-1 Convertible Crib", "Description": "Convertible wood crib that can be used as a toddler bed, daybed, and full-size headboard. Model numbers 657-N, 657-W, 657-E.", "Type": "Cribs and Cradles", "NumberOfUnits": "28,000"}],
        "Hazards": [{"Name": "The crib slats can loosen and detach, creating gaps that pose entrapment and suffocation hazards to infants.", "HazardType": "Suffocation"}],
        "Remedies": [{"Name": "Consumers should immediately stop using the recalled cribs and contact Dream On Me for a full refund or free replacement crib."}],
        "Manufacturers": [{"Name": "Dream On Me Industries Inc."}],
        "ManufacturerCountries": [{"Country": "China"}],
        "Images": [],
        "Injuries": [{"Name": "Dream On Me received 3 reports of slats loosening. No injuries."}],
        "_category": "cribs-cradles"
    },
    {
        "RecallNumber": "25-029",
        "RecallDate": "2025-02-05",
        "Title": "Britax Recalls Child Car Seats Due to Harness Issue",
        "URL": "https://www.cpsc.gov/Recalls/2025/britax-recalls-car-seats",
        "Description": "The harness chest clip can break under pressure.",
        "ConsumerContact": "Britax at 888-427-4829 or www.britax.com",
        "Products": [{"Name": "Britax Boulevard ClickTight Convertible Car Seat", "Description": "Convertible car seat for children 5 to 65 pounds. Model numbers E1C199T and E1C199V.", "Type": "Car Seats", "NumberOfUnits": "110,000"}],
        "Hazards": [{"Name": "The harness chest clip can crack or break during normal use, which could prevent the harness from properly restraining the child in a crash.", "HazardType": "Injury"}],
        "Remedies": [{"Name": "Consumers should contact Britax for a free replacement chest clip. Continue to use the car seat with the harness until the replacement clip arrives."}],
        "Manufacturers": [{"Name": "Britax Child Safety Inc."}],
        "ManufacturerCountries": [{"Country": "United States"}],
        "Images": [],
        "Injuries": [{"Name": "Britax received 23 reports of chest clips cracking. No injuries reported in crashes."}],
        "_category": "car-seats"
    },
    {
        "RecallNumber": "25-022",
        "RecallDate": "2025-01-25",
        "Title": "IKEA Recalls Children's Dressers Due to Tip-Over Hazard",
        "URL": "https://www.cpsc.gov/Recalls/2025/ikea-recalls-childrens-dressers",
        "Description": "Dressers can tip over if not properly anchored to the wall.",
        "ConsumerContact": "IKEA at 888-966-4532 or www.ikea.com",
        "Products": [{"Name": "IKEA KULLEN 3-Drawer Dresser", "Description": "Three-drawer dresser sold in white and birch effect. Article numbers 503.092.45 and 803.092.44.", "Type": "Children's Furniture", "NumberOfUnits": "200,000"}],
        "Hazards": [{"Name": "The dressers pose a serious tip-over and entrapment hazard if they are not properly anchored to the wall, which can result in death or injuries to children.", "HazardType": "Tip-Over"}],
        "Remedies": [{"Name": "Consumers who have not anchored the dresser should immediately place it in an area children cannot access and contact IKEA for a free wall-anchoring kit."}],
        "Manufacturers": [{"Name": "IKEA"}],
        "ManufacturerCountries": [{"Country": "Poland"}],
        "Images": [],
        "Injuries": [{"Name": "IKEA received 8 reports of tip-overs with these dressers. Two children required medical treatment."}],
        "_category": "furniture"
    },
    {
        "RecallNumber": "25-018",
        "RecallDate": "2025-01-15",
        "Title": "Target Recalls Cat & Jack Children's Pajamas Due to Burn Hazard",
        "URL": "https://www.cpsc.gov/Recalls/2025/target-recalls-cat-jack-pajamas",
        "Description": "Pajamas fail to meet federal flammability standards.",
        "ConsumerContact": "Target at 800-440-0680 or www.target.com",
        "Products": [{"Name": "Cat & Jack Fleece Pajama Sets", "Description": "Children's two-piece fleece pajama sets in sizes 4-12. UPC numbers starting with 492000.", "Type": "Children's Clothing", "NumberOfUnits": "65,000"}],
        "Hazards": [{"Name": "The children's pajamas fail to meet the federal flammability standards for children's sleepwear, posing a burn hazard to children.", "HazardType": "Burn"}],
        "Remedies": [{"Name": "Consumers should immediately stop using the recalled pajamas and return them to any Target store for a full refund."}],
        "Manufacturers": [{"Name": "Target Corporation"}],
        "ManufacturerCountries": [{"Country": "Bangladesh"}],
        "Images": [],
        "Injuries": [{"Name": "No injuries reported."}],
        "_category": "clothing"
    },
    {
        "RecallNumber": "24-312",
        "RecallDate": "2024-12-10",
        "Title": "Skip Hop Recalls Activity Centers Due to Choking Hazard",
        "URL": "https://www.cpsc.gov/Recalls/2024/skip-hop-recalls-activity-centers",
        "Description": "Small parts can detach from the activity center.",
        "ConsumerContact": "Skip Hop at 888-282-4747 or www.skiphop.com",
        "Products": [{"Name": "Skip Hop Explore & More Baby Activity Center", "Description": "3-stage activity center for babies 4 months and older. Model numbers 303325 and 303326.", "Type": "Toys", "NumberOfUnits": "53,000"}],
        "Hazards": [{"Name": "Small parts can break off from the toy attachments on the activity center, posing a choking hazard to young children.", "HazardType": "Choking"}],
        "Remedies": [{"Name": "Consumers should immediately remove the toy attachments and contact Skip Hop for free replacement toys."}],
        "Manufacturers": [{"Name": "Skip Hop Inc. (Carter's subsidiary)"}],
        "ManufacturerCountries": [{"Country": "China"}],
        "Images": [],
        "Injuries": [{"Name": "Skip Hop received 7 reports of parts breaking. One report of a child putting a piece in their mouth; no choking injuries."}],
        "_category": "toys"
    },
    {
        "RecallNumber": "24-298",
        "RecallDate": "2024-11-20",
        "Title": "Evenflo Recalls High Chairs Due to Fall Hazard",
        "URL": "https://www.cpsc.gov/Recalls/2024/evenflo-recalls-high-chairs",
        "Description": "The seat restraint can disengage allowing child to fall.",
        "ConsumerContact": "Evenflo at 800-233-5921 or www.evenflo.com",
        "Products": [{"Name": "Evenflo 4-in-1 Eat & Grow Convertible High Chair", "Description": "Convertible high chair, model numbers 28111234, 28111235. Sold at Walmart and Target from Jan 2023 to Oct 2024.", "Type": "High Chairs", "NumberOfUnits": "71,000"}],
        "Hazards": [{"Name": "The seat restraint buckle can become disengaged during use, posing a fall hazard to young children.", "HazardType": "Fall"}],
        "Remedies": [{"Name": "Consumers should immediately stop using the high chair and contact Evenflo for a free replacement restraint buckle."}],
        "Manufacturers": [{"Name": "Evenflo Company Inc."}],
        "ManufacturerCountries": [{"Country": "China"}],
        "Images": [],
        "Injuries": [{"Name": "Evenflo received 15 reports of buckles disengaging. Two reports of children falling; one bruise reported."}],
        "_category": "high-chairs"
    },
    {
        "RecallNumber": "24-275",
        "RecallDate": "2024-10-30",
        "Title": "Summer Infant Recalls Baby Gates Due to Fall Hazard",
        "URL": "https://www.cpsc.gov/Recalls/2024/summer-infant-recalls-baby-gates",
        "Description": "Mounting hardware can loosen causing gate to detach.",
        "ConsumerContact": "Summer Infant at 800-268-6237 or www.summerinfant.com",
        "Products": [{"Name": "Summer Infant Multi-Use Walk-Thru Gate", "Description": "Pressure-mounted baby gate, 28.5 to 48 inches wide. Model numbers 27190, 27191, 27193.", "Type": "Baby Gates", "NumberOfUnits": "45,000"}],
        "Hazards": [{"Name": "The pressure-mount hardware can loosen over time, causing the gate to detach from the doorway or stairway, posing a fall hazard to young children.", "HazardType": "Fall"}],
        "Remedies": [{"Name": "Consumers should immediately stop using the gate at the top of stairs and contact Summer Infant for a free hardware reinforcement kit."}],
        "Manufacturers": [{"Name": "Summer Infant Inc."}],
        "ManufacturerCountries": [{"Country": "China"}],
        "Images": [],
        "Injuries": [{"Name": "Summer Infant received 9 reports of gates detaching. Three reports of children falling down stairs; one required stitches."}],
        "_category": "baby-gates"
    },
    {
        "RecallNumber": "24-250",
        "RecallDate": "2024-10-05",
        "Title": "Nuna Recalls Baby Carriers Due to Buckle Failure",
        "URL": "https://www.cpsc.gov/Recalls/2024/nuna-recalls-baby-carriers",
        "Description": "Waist buckle can unlatch unexpectedly.",
        "ConsumerContact": "Nuna at 855-686-2628 or www.nunababy.com",
        "Products": [{"Name": "Nuna CUDL Clik Baby Carrier", "Description": "Soft structured baby carrier for infants 7-35 lbs. Sold in Caviar and Timber colors from March 2023 to August 2024.", "Type": "Baby Carriers", "NumberOfUnits": "18,000"}],
        "Hazards": [{"Name": "The waist buckle can unlatch unexpectedly during use, posing a fall hazard to the child.", "HazardType": "Fall"}],
        "Remedies": [{"Name": "Consumers should immediately stop using the carrier and contact Nuna for a free replacement buckle."}],
        "Manufacturers": [{"Name": "Nuna International BV"}],
        "ManufacturerCountries": [{"Country": "China"}],
        "Images": [],
        "Injuries": [{"Name": "Nuna received 4 reports of buckles unlatching. No injuries reported."}],
        "_category": "baby-carriers"
    },
    {
        "RecallNumber": "24-230",
        "RecallDate": "2024-09-15",
        "Title": "Philips Avent Recalls Baby Bottles Due to Choking Hazard",
        "URL": "https://www.cpsc.gov/Recalls/2024/philips-avent-recalls-baby-bottles",
        "Description": "The anti-colic valve can detach and pose a choking risk.",
        "ConsumerContact": "Philips at 800-542-8368 or www.philips.com/avent",
        "Products": [{"Name": "Philips Avent Anti-Colic Baby Bottles", "Description": "4oz and 9oz baby bottles with AirFree vent. Batch codes starting with AA23 printed on the bottom.", "Type": "Bottles and Feeding", "NumberOfUnits": "320,000"}],
        "Hazards": [{"Name": "The anti-colic insert valve can detach from the bottle during feeding, posing a choking hazard to infants.", "HazardType": "Choking"}],
        "Remedies": [{"Name": "Consumers should immediately stop using the bottles and contact Philips for free replacement bottles."}],
        "Manufacturers": [{"Name": "Philips Consumer Lifestyle"}],
        "ManufacturerCountries": [{"Country": "Netherlands"}],
        "Images": [],
        "Injuries": [{"Name": "Philips received 11 reports of valves detaching. Two reports of gagging; no choking injuries."}],
        "_category": "feeding"
    },
    {
        "RecallNumber": "24-210",
        "RecallDate": "2024-08-25",
        "Title": "Munchkin Recalls Bath Toys Due to Mold Hazard",
        "URL": "https://www.cpsc.gov/Recalls/2024/munchkin-recalls-bath-toys",
        "Description": "Squeeze bath toys can accumulate mold internally.",
        "ConsumerContact": "Munchkin at 800-344-2229 or www.munchkin.com",
        "Products": [{"Name": "Munchkin Ocean Squirts Bath Toys", "Description": "Set of 8 colorful rubber bath toys shaped like ocean animals. Sold from Jan 2022 to July 2024.", "Type": "Toys", "NumberOfUnits": "150,000"}],
        "Hazards": [{"Name": "Water can enter the toys through the squeeze hole and if not properly dried, mold can accumulate inside. Squeezing the toy can then expel mold-contaminated water, posing a health hazard to children.", "HazardType": "Mold/Health"}],
        "Remedies": [{"Name": "Consumers should immediately discard the bath toys and contact Munchkin for a coupon toward future purchase."}],
        "Manufacturers": [{"Name": "Munchkin Inc."}],
        "ManufacturerCountries": [{"Country": "China"}],
        "Images": [],
        "Injuries": [{"Name": "Munchkin received 20+ reports of mold inside toys. No injuries reported."}],
        "_category": "bath"
    },
]


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    out_file = DATA_DIR / "recalls.json"
    with open(out_file, "w") as f:
        json.dump(SAMPLE_RECALLS, f, indent=2)
    print(f"Created {len(SAMPLE_RECALLS)} sample recalls in {out_file}")


if __name__ == "__main__":
    main()
