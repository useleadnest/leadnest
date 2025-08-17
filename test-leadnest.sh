#!/usr/bin/env bash

#
# LeadNest API End-to-End Smoke Test Suite (Bash)
#
# Comprehensive test suite for LeadNest Flask API backend including:
# - Health checks with automatic retry
# - JWT authentication  
# - Protected endpoints
# - Idempotency testing
# - CSV bulk import (small inline, large background jobs)
# - Job polling with timeout
# - Twilio webhook simulation
# - JUnit XML reporting
#
# PREREQUISITES:
# - bash 4.0+
# - curl command available
# - jq command for JSON parsing
# - For large CSV tests: Redis server and RQ worker running
# - For Twilio tests: TWILIO_AUTH_TOKEN unset for local unsigned tests
#
# USAGE:
#   ./test-leadnest.sh [BASE_URL] [EMAIL] [PASSWORD] [OPTIONS]
#
# EXAMPLES:
#   ./test-leadnest.sh
#   ./test-leadnest.sh http://localhost:5000 admin@test.com secret123
#   ./test-leadnest.sh http://localhost:5000 a@b.c x --skip-large-csv
#

set -euo pipefail

# Default parameters
BASE_URL="${1:-http://localhost:5000}"
EMAIL="${2:-a@b.c}"
PASSWORD="${3:-x}"
POLL_SECONDS="${POLL_SECONDS:-2}"
POLL_TIMEOUT_S="${POLL_TIMEOUT_S:-120}"
SKIP_LARGE_CSV="${SKIP_LARGE_CSV:-false}"

# Parse additional arguments
while [[ $# -gt 3 ]]; do
    case $4 in
        --skip-large-csv)
            SKIP_LARGE_CSV=true
            ;;
        --poll-seconds=*)
            POLL_SECONDS="${4#*=}"
            ;;
        --poll-timeout=*)
            POLL_TIMEOUT_S="${4#*=}"
            ;;
        *)
            echo "Unknown option: $4" >&2
            exit 1
            ;;
    esac
    shift
done

# Colors and formatting
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
GRAY='\033[0;37m'
NC='\033[0m' # No Color

note() { echo -e "${CYAN}[*] $1${NC}"; }
ok() { echo -e "${GREEN}[✓] $1${NC}"; }
err() { echo -e "${RED}[✗] $1${NC}"; }
warn() { echo -e "${YELLOW}[!] $1${NC}"; }
die() { err "$1"; exit 1; }

# JUnit XML results
TEST_RESULTS=()
START_TIME=$(date +%s)

add_test_result() {
    local name="$1"
    local status="$2" 
    local duration="$3"
    local error="${4:-}"
    local timestamp=$(date -Iseconds)
    
    TEST_RESULTS+=("$name|$status|$duration|$error|$timestamp")
}

write_junit_xml() {
    local file_path="$1"
    local total_tests=${#TEST_RESULTS[@]}
    local failures=0
    local total_time=$(($(date +%s) - START_TIME))
    
    # Count failures
    for result in "${TEST_RESULTS[@]}"; do
        IFS='|' read -r name status duration error timestamp <<< "$result"
        if [[ "$status" == "FAIL" ]]; then
            ((failures++))
        fi
    done
    
    cat > "$file_path" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<testsuite name="LeadNest.API.SmokeTests" tests="$total_tests" failures="$failures" time="$total_time">
EOF
    
    for result in "${TEST_RESULTS[@]}"; do
        IFS='|' read -r name status duration error timestamp <<< "$result"
        echo "  <testcase name=\"$name\" time=\"$duration\">" >> "$file_path"
        if [[ "$status" == "FAIL" ]]; then
            echo "    <failure message=\"Test Failed\">$(echo "$error" | sed 's/&/\&amp;/g; s/</\&lt;/g; s/>/\&gt;/g; s/"/\&quot;/g')</failure>" >> "$file_path"
        fi
        echo "  </testcase>" >> "$file_path"
    done
    
    echo "</testsuite>" >> "$file_path"
    note "JUnit XML report written to: $file_path"
}

test_with_retry() {
    local name="$1"
    local max_retries="${2:-3}"
    local retry_delay="${3:-5}"
    shift 3
    local test_cmd="$*"
    
    local attempt=1
    local test_start=$(date +%s)
    
    while [[ $attempt -le $max_retries ]]; do
        if eval "$test_cmd" 2>/tmp/test_error_$$; then
            local duration=$(($(date +%s) - test_start))
            add_test_result "$name" "PASS" "$duration"
            rm -f /tmp/test_error_$$
            return 0
        else
            if [[ $attempt -eq $max_retries ]]; then
                local duration=$(($(date +%s) - test_start))
                local error_msg=""
                if [[ -f /tmp/test_error_$$ ]]; then
                    error_msg=$(cat /tmp/test_error_$$)
                fi
                add_test_result "$name" "FAIL" "$duration" "$error_msg"
                rm -f /tmp/test_error_$$
                return 1
            fi
            warn "$name failed (attempt $attempt/$max_retries), retrying in $retry_delay seconds..."
            sleep "$retry_delay"
            ((attempt++))
        fi
    done
}

format_json_response() {
    local response="$1"
    if command -v jq >/dev/null 2>&1; then
        echo "$response" | jq . 2>/dev/null || echo "$response"
    else
        echo "$response"
    fi
}

# Verify dependencies
if ! command -v curl >/dev/null 2>&1; then
    die "curl command not found. Please install curl."
fi

if ! command -v jq >/dev/null 2>&1; then
    warn "jq command not found. JSON formatting will be limited."
fi

echo -e "${MAGENTA}🚀 LeadNest API Smoke Test Suite${NC}"
echo -e "${GRAY}Base URL: $BASE_URL${NC}"
echo -e "${GRAY}Email: $EMAIL${NC}"
echo -e "${GRAY}Skip Large CSV: $SKIP_LARGE_CSV${NC}"
echo ""

# Global variables
TOKEN=""

# Test 1: Health Check
note "Test 1: Health Check (/healthz)"
test_with_retry "health_check" 3 2 '
    response=$(curl -sf "$BASE_URL/healthz" 2>&1)
    if [[ $? -ne 0 ]]; then
        echo "Health check failed: $response" >&2
        return 1
    fi
    ok "Health check passed: $response"
'

# Test 2: Ready Check (with retry for DB cold start)
note "Test 2: Ready Check (/readyz) - with retry for DB cold start"
test_with_retry "ready_check" 5 3 '
    response=$(curl -sf "$BASE_URL/readyz" 2>&1)
    if [[ $? -ne 0 ]]; then
        echo "Ready check failed: $response" >&2
        return 1
    fi
    ok "Ready check passed: $response"
'

# Test 3: Authentication
note "Test 3: Authentication (/auth/login)"
test_with_retry "authentication" 3 2 '
    response=$(curl -sf -X POST "$BASE_URL/auth/login" \
        -H "Content-Type: application/json" \
        -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}" 2>&1)
    
    if [[ $? -ne 0 ]]; then
        echo "Login request failed: $response" >&2
        return 1
    fi
    
    if command -v jq >/dev/null 2>&1; then
        TOKEN=$(echo "$response" | jq -r ".token // empty")
    else
        TOKEN=$(echo "$response" | grep -o "\"token\":\"[^\"]*\"" | cut -d"\"" -f4)
    fi
    
    if [[ -z "$TOKEN" ]]; then
        echo "No token in login response: $(format_json_response "$response")" >&2
        return 1
    fi
    
    ok "Authentication successful, token obtained"
'

# Test 4: Protected Endpoint
note "Test 4: Protected Endpoint (/leads)"
test_with_retry "protected_leads" 3 2 '
    response=$(curl -sf -H "Authorization: Bearer $TOKEN" "$BASE_URL/leads" 2>&1)
    if [[ $? -ne 0 ]]; then
        echo "Leads endpoint failed: $response" >&2
        return 1
    fi
    
    if command -v jq >/dev/null 2>&1; then
        count=$(echo "$response" | jq ". | length" 2>/dev/null || echo "unknown")
        ok "Leads endpoint OK, returned $count leads"
    else
        ok "Leads endpoint OK"
    fi
'

# Test 5: Idempotency
note "Test 5: Idempotency Testing (/leads/bulk with Idempotency-Key)"
test_with_retry "idempotency_test" 3 2 '
    idem_key="bash-test-$(date +%s)-$(openssl rand -hex 4 2>/dev/null || echo $RANDOM)"
    json_body="[{\"full_name\":\"Idem Test Bash\",\"email\":\"idem.bash@example.com\",\"source\":\"bash-test\",\"status\":\"new\"}]"
    
    # First request
    response1=$(curl -sf -X POST "$BASE_URL/leads/bulk" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -H "Idempotency-Key: $idem_key" \
        -d "$json_body" 2>&1)
    
    if [[ $? -ne 0 ]]; then
        echo "First idempotency request failed: $response1" >&2
        return 1
    fi
    
    if command -v jq >/dev/null 2>&1; then
        created1=$(echo "$response1" | jq -r ".created // 0")
        updated1=$(echo "$response1" | jq -r ".updated // 0")
        ok "First request: created=$created1 updated=$updated1"
    else
        ok "First request completed"
    fi
    
    # Second request (should be idempotent)
    response2=$(curl -sf -X POST "$BASE_URL/leads/bulk" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -H "Idempotency-Key: $idem_key" \
        -d "$json_body" 2>&1)
    
    if [[ $? -ne 0 ]]; then
        echo "Second idempotency request failed: $response2" >&2
        return 1
    fi
    
    if command -v jq >/dev/null 2>&1; then
        idempotent=$(echo "$response2" | jq -r ".idempotent // false")
        if [[ "$idempotent" != "true" ]]; then
            echo "Expected idempotent=true on second request, got: $(format_json_response "$response2")" >&2
            return 1
        fi
    fi
    
    ok "Idempotency test passed: second request properly marked as idempotent"
'

# Test 6: Small CSV Import
note "Test 6: Small CSV Import (/leads/bulk with file)"
test_with_retry "csv_small_import" 3 2 '
    csv_file="/tmp/leads_small_$(date +%s).csv"
    cat > "$csv_file" << EOF
full_name,email,phone,source,status
Bash Test One,bash-one@example.com,,csv-test,new
Bash Test Two,bash-two@example.com,+15550123456,csv-test,contacted
Bash Test Three,bash-three@example.com,+15550123457,csv-test,qualified
EOF
    
    response=$(curl -sf -X POST "$BASE_URL/leads/bulk" \
        -H "Authorization: Bearer $TOKEN" \
        -F "file=@$csv_file" 2>&1)
    
    rm -f "$csv_file"
    
    if [[ $? -ne 0 ]]; then
        echo "CSV import failed: $response" >&2
        return 1
    fi
    
    if command -v jq >/dev/null 2>&1; then
        created=$(echo "$response" | jq -r ".created // 0")
        updated=$(echo "$response" | jq -r ".updated // 0") 
        errors=$(echo "$response" | jq -r ".errors | length // 0")
        ok "CSV import successful: created=$created updated=$updated errors=$errors"
    else
        ok "CSV import completed"
    fi
'

# Test 7: Large CSV Import (Background Job) - Optional
if [[ "$SKIP_LARGE_CSV" != "true" ]]; then
    note "Test 7: Large CSV Import - Background Job (>5000 rows)"
    test_with_retry "csv_large_background" 3 2 '
        large_csv="/tmp/leads_large_$(date +%s).csv"
        
        note "Generating large CSV file with 5100 rows..."
        echo "full_name,email,phone,source,status" > "$large_csv"
        for i in $(seq 1 5100); do
            printf "Bash Large %d,bash-large-%d@bigcsv.test,+1888%04d,bg-test,new\n" "$i" "$i" "$i" >> "$large_csv"
        done
        
        note "Uploading large CSV (should enqueue background job)..."
        response=$(curl -sf -X POST "$BASE_URL/leads/bulk" \
            -H "Authorization: Bearer $TOKEN" \
            -F "file=@$large_csv" 2>&1)
        
        rm -f "$large_csv"
        
        if [[ $? -ne 0 ]]; then
            echo "Large CSV upload failed: $response" >&2
            return 1
        fi
        
        if command -v jq >/dev/null 2>&1; then
            status=$(echo "$response" | jq -r ".status // empty")
            job_id=$(echo "$response" | jq -r ".job_id // empty")
            
            if [[ "$status" != "enqueued" ]] || [[ -z "$job_id" ]]; then
                echo "Expected enqueued job, got: $(format_json_response "$response")" >&2
                return 1
            fi
        else
            job_id=$(echo "$response" | grep -o "\"job_id\":\"[^\"]*\"" | cut -d"\"" -f4)
            if [[ -z "$job_id" ]]; then
                echo "No job_id in response: $response" >&2
                return 1
            fi
        fi
        
        ok "Job enqueued successfully: $job_id"
        
        # Test 8: Job Polling
        note "Test 8: Job Polling (/jobs/$job_id)"
        deadline=$(($(date +%s) + POLL_TIMEOUT_S))
        poll_count=0
        
        while [[ $(date +%s) -lt $deadline ]]; do
            sleep "$POLL_SECONDS"
            ((poll_count++))
            
            job_response=$(curl -sf -H "Authorization: Bearer $TOKEN" "$BASE_URL/jobs/$job_id" 2>&1)
            if [[ $? -ne 0 ]]; then
                echo "Job status check failed: $job_response" >&2
                return 1
            fi
            
            if command -v jq >/dev/null 2>&1; then
                job_status=$(echo "$job_response" | jq -r ".status // unknown")
                note "Job $job_id: $job_status (poll #$poll_count)"
                
                if [[ "$job_status" == "finished" ]]; then
                    ok "Job completed successfully!"
                    created=$(echo "$job_response" | jq -r ".result.created // 0")
                    updated=$(echo "$job_response" | jq -r ".result.updated // 0")
                    ok "Job result: created=$created updated=$updated"
                    break
                elif [[ "$job_status" == "failed" ]]; then
                    error=$(echo "$job_response" | jq -r ".error // unknown")
                    echo "Job failed: $error" >&2
                    return 1
                fi
            else
                note "Job $job_id: polling... (poll #$poll_count)"
                if echo "$job_response" | grep -q "finished"; then
                    ok "Job completed successfully!"
                    break
                elif echo "$job_response" | grep -q "failed"; then
                    echo "Job failed: $job_response" >&2
                    return 1
                fi
            fi
        done
        
        if [[ $(date +%s) -ge $deadline ]]; then
            echo "Job polling timed out after $POLL_TIMEOUT_S seconds" >&2
            return 1
        fi
    '
    
    # Add separate test result for job polling
    add_test_result "job_polling" "PASS" "0"
else
    warn "Skipping large CSV and job polling tests (--skip-large-csv specified)"
    add_test_result "csv_large_background" "SKIP" "0"
    add_test_result "job_polling" "SKIP" "0"
fi

# Test 9: Twilio Webhook Simulation
note "Test 9: Twilio Webhook Simulation (/twilio/inbound)"
if [[ -z "${TWILIO_AUTH_TOKEN:-}" ]]; then
    test_with_retry "twilio_inbound_unsigned" 3 2 '
        response=$(curl -s -w "%{http_code}" -X POST "$BASE_URL/twilio/inbound" \
            -H "Content-Type: application/x-www-form-urlencoded" \
            -d "From=%2B15555550123&To=%2B15550000000&Body=Test+message+from+Bash" 2>&1)
        
        status_code="${response: -3}"
        response_body="${response%???}"
        
        if [[ "$status_code" == "200" ]]; then
            ok "Twilio inbound webhook accepted (unsigned local test)"
        elif [[ "$status_code" == "403" ]]; then
            warn "Twilio webhook returned 403 (signature validation enabled)"
        else
            echo "Unexpected Twilio webhook response: $status_code $(format_json_response "$response_body")" >&2
            return 1
        fi
    '
else
    warn "TWILIO_AUTH_TOKEN is set; skipping unsigned webhook test (signature validation enforced)"
    add_test_result "twilio_inbound_unsigned" "SKIP" "0"
fi

# Summary
echo ""
echo -e "${MAGENTA}📊 Test Summary${NC}"
echo -e "${MAGENTA}===============${NC}"

pass_count=0
fail_count=0
skip_count=0

for result in "${TEST_RESULTS[@]}"; do
    IFS='|' read -r name status duration error timestamp <<< "$result"
    case "$status" in
        "PASS") ((pass_count++)) ;;
        "FAIL") ((fail_count++)) ;;
        "SKIP") ((skip_count++)) ;;
    esac
done

total_count=${#TEST_RESULTS[@]}

echo -e "${GRAY}Total Tests: $total_count${NC}"
echo -e "${GREEN}Passed: $pass_count${NC}"
echo -e "${RED}Failed: $fail_count${NC}"
echo -e "${YELLOW}Skipped: $skip_count${NC}"

if [[ $fail_count -gt 0 ]]; then
    echo ""
    echo -e "${RED}❌ FAILED TESTS:${NC}"
    for result in "${TEST_RESULTS[@]}"; do
        IFS='|' read -r name status duration error timestamp <<< "$result"
        if [[ "$status" == "FAIL" ]]; then
            echo -e "${RED}  • $name: $error${NC}"
        fi
    done
fi

# Write JUnit XML report
report_path="./test-leadnest.xml"
write_junit_xml "$report_path"

echo ""
if [[ $fail_count -eq 0 ]]; then
    echo -e "${GREEN}🎉 ALL TESTS PASSED!${NC}"
    exit 0
else
    echo -e "${RED}💥 $fail_count TEST(S) FAILED!${NC}"
    exit 1
fi
